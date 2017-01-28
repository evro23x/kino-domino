import time
import tmdbsimple as tmdb
from requests.exceptions import HTTPError
from config import tmdb_api_key
from db_schema_tmdb import Movies_tmdb, db_session
from win_unicode_console import enable


enable()


def get_movie_id(user_input):
    movie = Movies_tmdb.query.filter(Movies_tmdb.title.ilike("%{}%".format(user_input[1:-1]))).first()
    if movie:
        return movie.id


def find_similiar_movie(movie_id):
    movie = Movies_tmdb.query.filter(Movies_tmdb.id == movie_id).first()
    result = Movies_tmdb.query.filter(Movies_tmdb.genre == movie.genre).all()
    max_matches = 0
    set_of_movie_keywords = {movie.keyword1, movie.keyword2, movie.keyword3, movie.keyword4, movie.keyword5,
    movie.keyword6, movie.keyword7, movie.keyword8, movie.keyword9, movie.keyword10}
    for each_movie in result:
        current_max_matches = 0
        set_of_each_movie_keywords = {each_movie.keyword1, each_movie.keyword2, each_movie.keyword3, each_movie.keyword4, 
        each_movie.keyword5, each_movie.keyword6, each_movie.keyword7, each_movie.keyword8, 
        each_movie.keyword9, each_movie.keyword10}
        current_max_matches = len(set_of_movie_keywords&set_of_each_movie_keywords)
        if current_max_matches > max_matches and each_movie.id != movie.id:
            max_matches = current_max_matches
            similliar_movie = each_movie.title
    try:
        return similliar_movie
    except UnboundLocalError:
        return "Я не смог ничего найти! ну и вкусы у тебя!"


def add_movies_to_DB(from_movie_id, to_movie_id):
    for movie_num in range(from_movie_id, to_movie_id):
        try:
            movie = tmdb.Movies(movie_num)
            response = movie.info(language="ru-RU")
            print(movie.title)
            key_words = movie.keywords()
            movie_to_add = Movies_tmdb(title=movie.title, genre=movie.genres[0]["name"], keyword1=key_words["keywords"][0]["name"],
                keyword2=key_words["keywords"][1]["name"],keyword3=key_words["keywords"][2]["name"],
                keyword4=key_words["keywords"][3]["name"],keyword5=key_words["keywords"][4]["name"],
                keyword6=key_words["keywords"][5]["name"],keyword7=key_words["keywords"][6]["name"],
                keyword8=key_words["keywords"][7]["name"],keyword9=key_words["keywords"][8]["name"],
                keyword10=key_words["keywords"][9]["name"])
            db_session.add(movie_to_add)
            time.sleep(1)
        except HTTPError:
            print("we've got 404!")
            continue
        except IndexError:
            print("we've got IndexError!")
            continue

    db_session.commit()
    

if __name__ == '__main__':
    tmdb.API_KEY = tmdb_api_key
    #add_movies_to_DB(251,300)
    user_input = ""
    print(find_similiar_movie(get_movie_id(user_input)))
    