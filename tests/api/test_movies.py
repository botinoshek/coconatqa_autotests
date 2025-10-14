import pytest
from Modul_4.Cinescope.api.api_manager import ApiManager

class TestMoviesAPI:
    def test_post_create_movies(self, api_manager: ApiManager, super_admin):
        """
        Тест на создание фильма.
        """
        response = super_admin.api.movies_api.post_create_movies()
        response_data = response.json()
        #тело запроса для сравнения с ответом
        sent_data = super_admin.api.movies_api.last_sent_data
        # Проверки
        assert response_data["name"] == sent_data["name"], 'name не совпадает'
        assert response_data["price"] == sent_data["price"], 'price не совпадает'
        assert response_data["description"] == sent_data["description"], 'description не совпадает'
        assert response_data["location"] == sent_data["location"], 'location не совпадает'
        assert response_data["published"] == sent_data["published"], 'published не совпадает'
        assert response_data["genreId"] == sent_data["genreId"], 'genreId не совпадает'

    def test_get_movies(self, api_manager: ApiManager):
        """
        Тест на просмотр афиш.
        """
        response = api_manager.movies_api.get_movies()
        response_data = response.json()

        # Проверки
        if response_data["movies"]:
            for movie in response_data["movies"]:
                # Обязательные поля фильма
                assert "id" in movie, "id отсутствует "
                assert "name" in movie, "name отсутствует"
                assert "description" in movie, "description отсутствует"
                assert "genreId" in movie, "genreId отсутствует"
                assert "imageUrl" in movie, "imageUrl отсутствует"
                assert "price" in movie, "price отсутствует "
                assert "rating" in movie, "rating отсутствует "
                assert "location" in movie, "location отсутствует"
                assert "published" in movie, "published отсутствует"
                assert "createdAt" in movie, "createdAt отсутствует"
                assert "genre" in movie, "genre отсутствует"

    @pytest.mark.parametrize("minPrice,maxPrice,locations,genreId", [
        (100, 200, "MSK", 1),
        (200, 300, "SPB", 2),
        (50, 150, "MSK,SPB", 3)
    ])
    def test_get_movies_par(self, api_manager: ApiManager, minPrice, maxPrice, locations, genreId):
        """
        Тест на просмотр афиш.
        """
        params = {
            'pageSize': 10,
            'page': 1,
            'minPrice': minPrice,
            'maxPrice': maxPrice,
            'locations': locations,
            'published': 'true',
            'genreId': genreId,
            'createdAt': 'asc'
        }
        response = api_manager.movies_api.get_movies(params=params)
        response_data = response.json()

        # Проверки
        if response_data["movies"]:
            for movie in response_data["movies"]:
                # Обязательные поля фильма
                assert "id" in movie, "id отсутствует "
                assert "name" in movie, "name отсутствует"
                assert "description" in movie, "description отсутствует"
                assert "genreId" in movie, "genreId отсутствует"
                assert "imageUrl" in movie, "imageUrl отсутствует"
                assert "price" in movie, "price отсутствует "
                assert "rating" in movie, "rating отсутствует "
                assert "location" in movie, "location отсутствует"
                assert "published" in movie, "published отсутствует"
                assert "createdAt" in movie, "createdAt отсутствует"
                assert "genre" in movie, "genre отсутствует"
    @pytest.mark.smoke
    def test_get_movies_id(self, api_manager: ApiManager, super_admin):
        """
        Cоздание фильма.
        """
        response = super_admin.api.movies_api.post_create_movies()
        response_data = response.json()
        movie_id = response_data["id"]
        #тело запроса для сравнения с ответом
        sent_data = super_admin.api.movies_api.last_sent_data

        """
        Тест на просмотр фильма по id.
        """
        response = api_manager.movies_api.get_movies_id(movie_id)
        response_data = response.json()

        # Проверки
        assert response_data["name"] == sent_data["name"], 'name не совпадает'
        assert response_data["price"] == sent_data["price"], 'price не совпадает'
        assert response_data["description"] == sent_data["description"], 'description не совпадает'
        assert response_data["location"] == sent_data["location"], 'location не совпадает'
        assert response_data["published"] == sent_data["published"], 'published не совпадает'
        assert response_data["genreId"] == sent_data["genreId"], 'genreId не совпадает'

    @pytest.mark.parametrize("overrides", [
        {"price": 0},
        {"published": False},
        {"genreId": 5},
    ])
    def test_delete_movies_id(self, api_manager: ApiManager, super_admin, overrides):
        """
        Cоздание фильма.
        """
        response = super_admin.api.movies_api.post_create_movies()
        response_data = response.json()
        movie_id = response_data["id"]
        #тело запроса для сравнения с ответом
        sent_data = super_admin.api.movies_api.last_sent_data

        """
        Тест на удаление фильма по id.
        """
        response = super_admin.api.movies_api.delete_movies_id(movie_id)
        response_data = response.json()

        """
        проверка что фильм удален
        """
        get_id = api_manager.movies_api.get_movies_id(movie_id, expected_status=404)
        get_id_data = get_id.json()
        expected_error = {'message': 'Фильм не найден', 'error': 'Not Found', 'statusCode': 404}

        # Проверки
        assert get_id.status_code == 404, "фильм найден"
        assert get_id_data == expected_error
        assert response_data["name"] == sent_data["name"], 'name не совпадает'
        assert response_data["price"] == sent_data["price"], 'price не совпадает'
        assert response_data["description"] == sent_data["description"], 'description не совпадает'
        assert response_data["location"] == sent_data["location"], 'location не совпадает'
        assert response_data["published"] == sent_data["published"], 'published не совпадает'
        assert response_data["genreId"] == sent_data["genreId"], 'genreId не совпадает'
    @pytest.mark.smoke
    def test_patch_movies_id(self, api_manager: ApiManager, super_admin):
        """
        Cоздание фильма.
        """
        response = super_admin.api.movies_api.post_create_movies()
        response_data = response.json()
        movie_id = response_data["id"]
        """
        Тест на изменение фильма по id.
        """
        response = super_admin.api.movies_api.patch_movies_id(movie_id)
        updated_data = response.json()
        #Измененное тело запроса для сравнения с ответом
        patch_data = super_admin.api.movies_api.patch_sent_data

        # Проверки
        assert updated_data["name"] == patch_data["name"], f'name: {updated_data["name"]} != {patch_data["name"]}'
        assert updated_data["price"] == patch_data["price"], f'price: {updated_data["price"]} != {patch_data["price"]}'
        assert updated_data["description"] == patch_data["description"], f'description: {updated_data["description"]} != {patch_data["description"]}'
        assert updated_data["location"] == patch_data["location"], f'location: {updated_data["location"]} != {patch_data["location"]}'
        assert updated_data["published"] == patch_data["published"], f'published: {updated_data["published"]} != {patch_data["published"]}'
        assert updated_data["genreId"] == patch_data["genreId"], f'genreId: {updated_data["genreId"]} != {patch_data["genreId"]}'
        assert updated_data["imageUrl"] == patch_data["imageUrl"], f'imageUrl: {updated_data["imageUrl"]} != {patch_data["imageUrl"]}'
    @pytest.mark.regression
    def test_negative_post_create_movies(self, api_manager: ApiManager, common_user):
        """
        Тест на создание фильма с негативным сценарием.
        """
        response = common_user.api.movies_api.negative_post_create_movies()
        response_data = response.json()

        expected_errors = {
            "message": "Forbidden resource",
            "error": "Forbidden",
            "statusCode": 403
        }
        #проверки
        assert response_data == expected_errors, 'Тело ошибки не совпадает'

    def test_negative_get_movies(self, api_manager: ApiManager):
        """
        Тест на просмотр афиш с негативным сценарием.
        """
        response = api_manager.movies_api.negative_get_movies()
        response_data = response.json()

        expected_errors = {'message': ['Поле pageSize имеет максимальную величину 20',
                                       'Поле pageSize имеет минимальную величину 1',
                                       'Поле pageSize должно быть числом',
                                       'Поле page имеет минимальную величину 1',
                                       'Поле page должно быть числом',
                                       'Поле minPrice имеет минимальную величину 1',
                                       'Поле minPrice должно быть числом',
                                       'Поле minPrice имеет минимальную величину 1'],
                           'error': 'Bad Request', 'statusCode': 400}
        # Проверки
        assert response_data == expected_errors, 'Тело ошибки не совпадает'

    def test_negative_get_movies_id(self, api_manager: ApiManager, super_admin):
        """
        Тест на просмотр фильма по id с негативным сценарием.
        """
        response = super_admin.api.movies_api.negative_get_movies()
        response_data = response.json()
        expected_errors = {'message': ['Поле pageSize имеет максимальную величину 20',
                                       'Поле pageSize имеет минимальную величину 1',
                                       'Поле pageSize должно быть числом',
                                       'Поле page имеет минимальную величину 1',
                                       'Поле page должно быть числом',
                                       'Поле minPrice имеет минимальную величину 1',
                                       'Поле minPrice должно быть числом',
                                       'Поле minPrice имеет минимальную величину 1'],
                           'error': 'Bad Request', 'statusCode': 400}
        # Проверки
        assert response_data == expected_errors, 'Тело ошибки не совпадает'

    def test_negative_delete_movies_id(self, api_manager: ApiManager, super_admin):
        """
        Тест на удаление фильма по id с негативным сценарием.
        """
        response = super_admin.api.movies_api.negative_delete_movies_id()
        response_data = response.json()
        print(response_data)
        expected_errors = {'message': 'Фильм не найден',
                           'error': 'Not Found',
                           'statusCode': 404}
        # Проверки
        assert response_data == expected_errors, 'Тело ошибки не совпадает'

    def test_negative_patch_movies_id(self, api_manager: ApiManager, super_admin):
        """
        Cоздание фильма.
        """
        response = super_admin.api.movies_api.post_create_movies()
        response_data = response.json()
        movie_id = response_data["id"]

        """
        Тест на изменение фильма по id с негативным сценарием.
        """
        response = super_admin.api.movies_api.negative_patch_movies_id(movie_id)
        updated_data = response.json()

        # Проверки
        expected_error = {'message': ['Поле description должно быть строкой',
                                      'price must not be less than 1',
                                      'Поле price должно быть числом',
                                      'location must be one of the following values: MSK, SPB',
                                      'Поле published должно быть булевым значением',
                                      'genreId must not be less than 1', 'Поле genreId должно быть числом'],
                          'error': 'Bad Request', 'statusCode': 400}

        assert updated_data == expected_error