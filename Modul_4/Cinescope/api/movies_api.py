from custom_requester.custom_requester import CustomRequester
from faker import Faker
from utils.factories.movie_factory import movie_factory
from utils.data_generator import DataGenerator

faker = Faker("Ru_ru")
faker_patch = Faker("Ru_ru")
generate_location = DataGenerator.generate_location()

class MoviesAPI(CustomRequester):
    """
    Класс для работы с API фильмов.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=session.base_url)
        self.session = session

    def post_create_movies(self, data=None, expected_status=201):
        """
        Создание фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        data_movies = data or movie_factory()

        self.last_sent_data = data_movies.copy()

        return self.send_request(
            method="post",
            endpoint="movies",
            data= data_movies,
            expected_status=expected_status
        )

    def get_movies(self, params=None,  expected_status=200):
        """
        Получение афиш.
        :param expected_status: Ожидаемый статус-код.
        """
        params = {
            'pageSize': 10,
            'page': 1,
            'minPrice': 1,
            'maxPrice': 1000,
            'locations': generate_location,
            'published': 'true',
            'genreId': faker.random_int(1, 10),
            'createdAt': 'asc'
        }

        return self.send_request(
            method="get",
            endpoint=f"movies",
            expected_status=expected_status,
            params = params
        )

    def get_movies_id(self, movie_id, expected_status=200):
        """
        Получение фильма по id.
        :param expected_status: Ожидаемый статус-код.
        :param id: ожидает id фильма
        """
        return self.send_request(
            method="get",
            endpoint=f"movies/{movie_id}",
            expected_status=expected_status
        )

    def delete_movies_id(self, movie_id, expected_status=200):
        """
        Удаление фильма по id.
        :param expected_status: Ожидаемый статус-код.
        :param id: ожидает id фильма
        """
        return self.send_request(
            method="delete",
            endpoint=f"movies/{movie_id}",
            expected_status=expected_status
        )

    def patch_movies_id(self, movie_id, expected_status=200):
        """
        Изменение фильма по id.
        :param expected_status: Ожидаемый статус-код.
        :param id: ожидает id фильма
        """
        patch_data_movies = {
            "name": f"{faker_patch.word()}",
            "description": f"{faker_patch.text()}",
            "price": faker_patch.random_int(1, 200) ,
            "location": f"{generate_location}",
            "imageUrl": f"{faker_patch.image_url(width=300, height=200)}",
            "published": faker_patch.boolean(),
            "genreId": faker_patch.random_int(1, 10),
        }

        self.patch_sent_data = patch_data_movies.copy()

        return self.send_request(
            method="patch",
            endpoint=f"movies/{movie_id}",
            data=patch_data_movies,
            expected_status=expected_status
        )

    def negative_post_create_movies(self, expected_status=403):
        """
        Создание фильма c неверным юзером.
        :param expected_status: Ожидаемый статус-код.
        """
        data_movies = {
            "name": f"{faker.word()} {faker_patch.word()}",
            "imageUrl": f"{faker.image_url(width=300, height=200)}",
            "price": faker.random_int(1, 200) ,
            "description": f"{faker.text()}",
            "location": f"{generate_location}",
            "published": faker.boolean(),
            "genreId": faker.random_int(1, 10),
        }

        self.last_sent_data = data_movies.copy()

        return self.send_request(
            method="post",
            endpoint="movies",
            data= data_movies,
            expected_status=expected_status
        )

    def negative_get_movies(self,  expected_status=400):
        """
        Получение афиш с неверным форматом.
        :param expected_status: Ожидаемый статус-код.
        """
        # TODO: оптимизировать параметр params для точных проверок в тесте
        params = f'?pageSize=фф&page=в&minPrice=п&maxPrice=one&locations=МСК&published=тру&genreId=1&createdAt=asc'

        return self.send_request(
            method="get",
            endpoint=f"movies{params}",
            expected_status=expected_status
        )

    def negative_get_movies_id(self, expected_status=404):
        """
        Получение фильма понеизвестному id.
        :param expected_status: Ожидаемый статус-код.
        :param id: ожидает id фильма
        """
        movie_id = faker.word()

        return self.send_request(
            method="get",
            endpoint=f"movies/{movie_id}",
            expected_status=expected_status
        )

    def negative_delete_movies_id(self, expected_status=404):
        """
        Удаление фильма с неверным id.
        :param expected_status: Ожидаемый статус-код.
        """
        #неверный айди для проверки
        movie_id = faker.word()

        return self.send_request(
            method="delete",
            endpoint=f"movies/{movie_id}",
            expected_status=expected_status
        )

    def negative_patch_movies_id(self, movie_id, expected_status=400):
        """
        Изменение фильма id с неверными параметрами.
        :param expected_status: Ожидаемый статус-код.
        :param id: ожидает id фильма
        """
        patch_data_movies = {
            "name": "None",
            "description": 123,
            "price": "fsdfasd" ,
            "location": "МСК",
            "imageUrl": f"{faker_patch.image_url(width=300, height=200)}",
            "published": "null",
            "genreId": "Null",
        }

        self.patch_sent_data = patch_data_movies.copy()

        return self.send_request(
            method="patch",
            endpoint=f"movies/{movie_id}",
            data=patch_data_movies,
            expected_status=expected_status
        )