import time
import tmdbsimple as tmdb
from requests.exceptions import HTTPError
from sqlalchemy import exists
from config import tmdb_api_key
from db_schema_tmdb import Movies_tmdb, db_session, PlotKeyword, MoviesKeywords
from win_unicode_console import enable


enable()


def get_movie_id(user_input):
    movie = Movies_tmdb.query.filter(Movies_tmdb.title.ilike("%{}%".format(user_input[1:-1]))).first()
    if movie:
        return movie.id


def find_similiar_movie(movie_id_):
    movie = Movies_tmdb.query.filter(Movies_tmdb.id == movie_id_).first()
    same_genre_movies = Movies_tmdb.query.filter(Movies_tmdb.genre == movie.genre).all()
    max_matches = 0
    movie_keywords_ids = MoviesKeywords.query.filter(MoviesKeywords.movie_id == movie_id_).all()
    set_movie_keywords_ids = set()
    for keyword in movie_keywords_ids:
        set_movie_keywords_ids.add(keyword.keyword_id)
    for each_movie in same_genre_movies:
        current_max_matches = 0
        each_movie_keywords_ids = MoviesKeywords.query.filter(MoviesKeywords.movie_id == each_movie.id).all()
        set_of_each_movie_keywords_ids = set()
        for keyword in each_movie_keywords_ids:
            set_of_each_movie_keywords_ids.add(keyword.keyword_id)
        current_max_matches = len(set_movie_keywords_ids&set_of_each_movie_keywords_ids)
        if current_max_matches > max_matches and each_movie.id != movie_id_:
            max_matches = current_max_matches
            similliar_movie = each_movie.title
    try:
        return similliar_movie
    except UnboundLocalError:
        return "Я не смог ничего найти! ну и вкусы у тебя!"


def add_keywords_and_movie_to_associatve_table(movie, key_words):
    movie_to_add_id = Movies_tmdb.query.filter(Movies_tmdb.title == movie).first().id
    for key_word in key_words["keywords"]:
        key_word_id = PlotKeyword.query.filter(PlotKeyword.keyword == key_word["name"]).first().id
        row_to_index_table = MoviesKeywords(movie_id=movie_to_add_id, keyword_id=key_word_id)
        db_session.add(row_to_index_table)
    db_session.commit()


def add_movies_to_DB(from_movie_id, to_movie_id):
    for movie_num in range(from_movie_id, to_movie_id):
        try:
            print(movie_num)
            movie = tmdb.Movies(movie_num)
            response = movie.info(language="ru-RU")
            print(movie.title)
            movie_to_add = Movies_tmdb(title=movie.title, genre=movie.genres[0]["name"])
            db_session.add(movie_to_add)
            key_words = movie.keywords()
            for key_word in key_words["keywords"]:
                (ret, ), = db_session.query(exists().where(PlotKeyword.keyword == key_word["name"]))
                if ret:
                    continue
                else:
                    key_word_to_add = PlotKeyword(keyword=key_word["name"])
                    db_session.add(key_word_to_add)
            db_session.commit()
            add_keywords_and_movie_to_associatve_table(movie.title, key_words)
            time.sleep(1)
        except HTTPError:
            print("we've got 404!")
            continue
        except IndexError:
            print("we've got IndexError!")
            continue
    

if __name__ == '__main__':
    tmdb.API_KEY = tmdb_api_key
    #add_movies_to_DB(50,150)
    #user_input = "побег"
    #print(find_similiar_movie(get_movie_id(user_input)))
    #movie = tmdb.Movies(3)
    #response = movie.info(language="ru-RU")
    user_input = "бегущий"
    print(find_similiar_movie(get_movie_id(user_input)))