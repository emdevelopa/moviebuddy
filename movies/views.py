from django.shortcuts import render
import requests
import os
from dotenv import load_dotenv, find_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer


def get_imdb_data(imdb_url, imdb_params, fields):
    load_dotenv(find_dotenv())
    imdb_params['apiKey'] = 'k_3ksfua4o'
    response = requests.get(imdb_url, params=imdb_params)
    data = response.json()
    if 'errorMessage' in data:
        raise Exception(f"Error from IMDb API: {data['errorMessage']}")
    results = data['items']
    print(results)
    return [{field: result[field] for field in fields} for result in results]





class MovieDetails(APIView):
    def get(self, request):
        title = request.GET.get('title')
        imdb_url = 'https://imdb-api.com/API/AdvancedSearch/'
        imdb_params = {'expression': 'movie', 'title': title, 'plot': 'full'}
        response = requests.get(imdb_url, params=imdb_params)
        data = response.json()
        if data['errorMessage']:
            return Response({'message': 'Movie not found.'})
        results = data['results']
        movie_data = []
        for result in results:
            movie_data.append({
                'title': result['title'],
                'plot': result['plot'],
                'year': result['year'],
                'genres': result['genres'],
                'runtime': result['runtimeStr'],
                'rating': result['imDbRating'],
                'cast': result['stars'],
                'poster': result['image']
            })
        return Response({'movie_data': movie_data})
    
class MovieList(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        genre = request.GET.get('genre')
        imdb_url = 'https://imdb-api.com/API/MostPopularMovies/k_b4cfp83v'
        imdb_params = {}
        if genre:
            imdb_params['genre'] = genre
        fields = ['title', 'image']

        imdb_response = requests.get(imdb_url, params=imdb_params)
        imdb_response.raise_for_status()
        imdb_data = imdb_response.json()
        
        if imdb_data['items']:
            movies = []
            count = 0
            for movie in imdb_data['items']:
                if count == 5:
                    break
                title = movie['title']
                movie_url = f'http://www.omdbapi.com/?t={title}&apikey=f73240e0&plot=full'
                movie_response = requests.get(movie_url)
                movie_response.raise_for_status()
                movie_data = movie_response.json()
                if movie_data['Response'] == 'False':
                    try:
                        raise Exception(f'{movie_data["Error"]} for "{title}"')
                    except Exception as e:
                        return Response({'message': str(e)})
                else:
                    movies.append({
                        'name': movie_data['Title'],
                        'url': f'https://www.netflix.com/search?q={title.replace(" ", "+")}',
                        'image': movie_data['Poster'],
                        'plot': movie_data['Plot'],
                        'rating': movie_data['imdbRating']
                    })
                    count += 1
            return Response({'recommendations': movies})
            print(Response)
        else:
            try:
                raise Exception('No movies found with the given criteria')
            except Exception as e:
                return Response({'message': str(e)})




def get_movie_data(title):
    imdb_url = 'https://imdb-api.com/API/SearchMovie/'
    imdb_params = {'expression': title}
    response = requests.get(imdb_url, params=imdb_params)
    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            # If there is no JSON data, return an error message
            return {'error': 'No JSON data found.'}
        if data['errorMessage']:
            # If there is an error message, return it
            return {'error': data['errorMessage']}
        results = data['results']
        if len(results) == 0:
            # If there are no results, return an error message
            return {'error': 'No results found.'}
        # Get the IMDB ID for the first result
        imdb_id = results[0]['id']
        imdb_url = 'https://imdb-api.com/API/Title/'
        imdb_params = {'apiKey': 'k_3ksfua4o', 'id': imdb_id, 'plot': 'full'}
        response = requests.get(imdb_url, params=imdb_params)
        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError:
                # If there is no JSON data, return an error message
                return {'error': 'No JSON data found.'}
            if data['errorMessage']:
                # If there is an error message, return it
                return {'error': data['errorMessage']}
            # Extract the relevant movie data
            movie_data = {
                'title': data['title'],
                'plot': data['plot'],
                'year': data['year'],
                'genres': data['genres'],
                'runtime': data['runtimeStr'],
                'rating': data['imDbRating'],
                'cast': data['stars'],
                'poster': data['image'],
            }
            return [movie_data]
        else:
            # If there is an HTTP error, return an error message
            return {'error': 'HTTP error.'}
    else:
        # If there is an HTTP error, return an error message
        return {'error': 'HTTP error.'}


class RecommendMovies(APIView):
    def get(self, request):
        user_rating = request.GET.get('user_rating')
        genre = request.GET.get('genre')
        year = request.GET.get('year')
        imdb_url = 'https://imdb-api.com/API/AdvancedSearch/'
        imdb_params = {'expression': 'movie'}
        if user_rating:
            imdb_params['userRating'] = user_rating
        if genre:
            imdb_params['genre'] = genre
        if year:
            imdb_params['productionYear'] = year
        fields = ['title', 'image']
        imdb_data = get_imdb_data(imdb_url, imdb_params, fields)
        if imdb_data:
            movie = imdb_data[0]
            imdb_title = movie['title']
            imdb_image = movie['image']
            imdb_plot = movie['plot']
            imdb_rating = movie['imDb']
            netflix_url = f'https://www.netflix.com/search?q={imdb_title.replace(" ", "+")}'
            return Response({
                'name': imdb_title,
                'url': netflix_url,
                'image': imdb_image,
                'plot': imdb_plot,
                'rating': imdb_rating
            })
        else:
            return Response({'message': 'No movies found with the given criteria'})


def movies_by_genre(request, genre):
    movies = Movie.objects.filter(genre=genre)
    data = {
        'movies': [
            {
                'title': movie.title,
                'description': movie.description,
                'genre': movie.genre,
                'release_date': movie.release_date.strftime('%Y-%m-%d'),
                'poster': movie.poster.url,
            }
            for movie in movies
        ]
    }
    return JsonResponse(data)




def index(request):
    return render(request, "index.html")

def movielist(request):
    return render(request, 'index.html')
