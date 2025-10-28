from tkinter.font import names

import psycopg2
import sqlalchemy
from Modul_4.Cinescope.api.api_manager import ApiManager
from faker import Faker

from Modul_4.Cinescope.api.movies_api import faker


class TestDBMovies:
    def test_post_create_movies_db(self, api_manager: ApiManager, super_admin, db_helper):
        """
        Тест на создание и удаление фильма и проверка в базе данных.
        """
        name_movie = f"{faker.word()}_test_db"
        assert db_helper.get_movie_by_name(name_movie) is None #проверка что фильм по названию заранее не существует
        response = super_admin.api.movies_api.post_create_movies(name=name_movie)
        response_data = response.json()
        movie_id = response_data["id"]
        movie = db_helper.get_movie_by_name(name_movie)
        assert movie is not None
        assert movie.name == name_movie
        #удаляем
        response = super_admin.api.movies_api.delete_movies_id(movie_id)
        assert db_helper.get_movie_by_name(name_movie) is None

