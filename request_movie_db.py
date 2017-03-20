import time
from datetime import datetime, timedelta
import tmdbsimple as tmdb
from requests.exceptions import HTTPError
from sqlalchemy import exists, exc
from config import tmdb_api_key
from db_schema import db_session, PlotKeyword, MoviesKeywords, Movies, TimeSlots
from win_unicode_console import enable
# import pprint
enable()


# @profile
def get_movie_id(user_input):
    movie = Movies.query.filter(Movies.title.ilike("%{}%".format(user_input))).first()
    if movie:
        return movie.id


# @profile
def get_plot_keywords_ids_by_movie_id(movie_id):
    return [r[0] for r in db_session.query(MoviesKeywords.keyword_id).filter(MoviesKeywords.movie_id == movie_id).all()]


# @profile
def find_similar_movie(movie_id):
    movie = Movies.query.filter(Movies.id == movie_id).first()
    same_genre_movies = Movies.query.filter(Movies.genre == movie.genre,
                                            Movies.rating.between(movie.rating - 1.5, movie.rating + 1.5)).all()
    max_matches = 0
    similar_movie_title = None
    movie_keywords_ids = get_plot_keywords_ids_by_movie_id(movie_id)
    set_movie_keywords_ids = set(movie_keywords_ids)
    for each_movie in same_genre_movies:
        current_max_matches = 0
        each_movie_keywords_ids = get_plot_keywords_ids_by_movie_id(each_movie.id)
        current_max_matches = len(set_movie_keywords_ids.intersection(set(each_movie_keywords_ids)))
        if current_max_matches > max_matches and each_movie.id != movie_id:
            max_matches = current_max_matches
            similar_movie_title = each_movie.title

    return similar_movie_title


def add_plot_keywords_in_database(key_words):
    for key_word in key_words["keywords"]:
        is_keyword_in_database = db_session.query(exists().where(PlotKeyword.keyword == key_word["name"]))[0][0]
        if not is_keyword_in_database:
            key_word_to_add = PlotKeyword(keyword=key_word["name"])
            db_session.add(key_word_to_add)
    db_session.commit()


def get_info_about_movie(tmdb_id):
    movie = tmdb.Movies(tmdb_id)
    try:
        response = movie.info(language="ru-RU")
    except HTTPError:
        movie = None
    return movie


def get_movie_info_from_tmdb_by_movie_title(movie_title):
    search = tmdb.Search()
    response = search.movie(query=movie_title, language="ru-RU")
    if len(search.results) == 0:
        return None

    movie_id = search.results[0]["id"]
    movie = get_info_about_movie(movie_id)
    if movie is None:
        return None

    genre = ""
    if len(movie.genres) > 0:
        genre = movie.genres[0]["name"]

    movie_info = {"genre": genre,
                  "duration": movie.runtime,
                  "rating": movie.vote_average,
                  "description": search.results[0]["overview"]}
    return movie_info


def request_info_from_tmdb_and_store_in_database(movie_title):
    try:
        search = tmdb.Search()
        response = search.movie(query=movie_title, language="ru-RU")
        movie_id = search.results[0]["id"]
        movie = get_info_about_movie(movie_id)
        us_release_date = movie.releases()["countries"][0]["release_date"]
        check_if_movie_exists_if_not_add(movie, us_release_date)
    except exc.IntegrityError:
        print("Something went very wrong!")
        db_session.rollback()
    except IndexError:
        print("Index Error!")


def add_keywords_and_movie_to_associatve_table(movie_to_add_id, key_words):
    for key_word in key_words["keywords"]:
        key_word_id = PlotKeyword.query.filter(PlotKeyword.keyword == key_word["name"]).first().id
        row_to_index_table = MoviesKeywords(movie_id=movie_to_add_id, keyword_id=key_word_id)
        db_session.add(row_to_index_table)
    db_session.commit()


def check_if_movie_exists_if_not_add(movie, us_release_date):
    try:
        if movie.runtime is None:
            movie.runtime = 0
        check_movie_exist = db_session.query(Movies).filter_by(title=movie.title,
                                                               genre=movie.genres[0]["name"],
                                                               duration=movie.runtime,
                                                               start_date=us_release_date).first()
        if check_movie_exist:
            if check_movie_exist.rating != movie.vote_average:
                db_session.query(Movies).filter_by(id=check_movie_exist.id).update({"rating": movie.vote_average})
        else:
            movie_to_add = Movies(title=movie.title, genre=movie.genres[0]["name"],
                                  duration=movie.runtime, rating=movie.vote_average, start_date=us_release_date)
            db_session.add(movie_to_add)
            key_words = movie.keywords()
            add_plot_keywords_in_database(key_words)
            add_keywords_and_movie_to_associatve_table(movie_to_add.id, key_words)
    except IndexError:
        print("Index Error!")


def add_movies_to_database(from_movie_id, to_movie_id):
    for movie_num in range(from_movie_id, to_movie_id):
        try:
            print(movie_num)
            movie = get_info_about_movie(movie_num)
            print(movie.title)
            us_release_date = movie.releases()["countries"][0]["release_date"]
            check_if_movie_exists_if_not_add(movie, us_release_date)
            time.sleep(1)
        except HTTPError:
            print("we've got 404!")
            continue
        except exc.IntegrityError:
            print("we've got Duplicate!")
            db_session.rollback()
            continue
        except IndexError:
            print("Index Error!")
            continue


def get_current_movies():
    all_time_slots = TimeSlots.query.filter(TimeSlots.time.between(datetime.now(),
                                                                   datetime.now() + timedelta(days=3))).all()
    current_movies = []
    for slot in all_time_slots:
        if not slot.movie in current_movies:
            current_movies.append(slot.movie)
    return current_movies


def get_similar_movies_for_list_of_movies(current_movies):
    similar_movies = []
    for each_movie in current_movies:
        movie_title = each_movie.title
        search = tmdb.Search()
        response = search.movie(query=movie_title, language="ru-RU")
        if search.results:
            movie_id = search.results[0]["id"]
            movie = get_info_about_movie(movie_id)
            get_similar_movies_from_tmdb = movie.similar_movies(language="ru-RU")
            for similar_movie in get_similar_movies_from_tmdb["results"]:
                if not similar_movie["title"] in similar_movies:
                    similar_movies.append(similar_movie["title"])
    return similar_movies


def add_similar_movies(similar_movies):
    for movie_title in similar_movies:
        print(movie_title)
        request_info_from_tmdb_and_store_in_database(movie_title)
        time.sleep(1)


def find_and_add_similar_movies_to_current_movies():
    current_movies = get_current_movies()
    similar_movies = get_similar_movies_for_list_of_movies(current_movies)
    add_similar_movies(similar_movies)


def get_movie_titles_from_database_by_id(min_id, max_id):
    return [movie for movie in db_session.query(Movies).filter(Movies.id >= min_id).filter(Movies.id <= max_id).all()]


def find_and_add_similar_movies_to_movies_in_database_by_id(min_id, max_id):
    movies = get_movie_titles_from_database_by_id(min_id, max_id)
    similar_movies = get_similar_movies_for_list_of_movies(movies)
    print(similar_movies)
    add_similar_movies(similar_movies)


if __name__ == '__main__':
    tmdb.API_KEY = tmdb_api_key
    # add_movies_to_database(1780, 1800)
    # user_input = "бегущий по лезвию"
    # print(user_input)
    # print(get_movie_id(user_input))
    # print(find_similar_movie(get_movie_id(user_input)))
    # user_input2 = "Дневник Бриджет Джонс"
    # print(user_input2)
    # print(get_movie_id(user_input2))
    # print(find_similar_movie(get_movie_id(user_input2)))
    # find_and_add_similar_movies_to_current_movies()
    # find_and_add_similar_movies_to_movies_in_database_by_id(200, 220)
