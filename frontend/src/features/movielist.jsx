import React, { useState, useEffect } from 'react';

function MovieList() {
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    fetch('/movies/movielist')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong');
        }
      })
      .then(data => {
        setMovies(data.recommendations);
      })
      .catch(error => console.error(error));
    }, []);
    console.log(movies)

  return (
    <div>
      <h1>All Movies</h1>
      {movies.map((movie, index) => (
        <div key={index}>
          <h2>{movie.name}</h2>
          <img src={movie.image} alt={movie.name} />
          <p>{movie.plot}</p>
          <p>Rating: {movie.rating}</p>
        </div>
      ))}
    </div>
  );
}

export default MovieList;
