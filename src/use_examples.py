import re
from utils import *
import pandas as pd
from recommenders.popularity_recommender import PopularityRecommender
from recommenders.content_recommender import ContentRecommender
from recommenders.collaborative_recommender import CollabRecommender
from recommenders.hybrid_recommender import HybridRecommender
from recommenders.profile_builder import ProfileBuilder
from csv_processes import anime, ratings

# data
print(ratings.head())


# content stuff
item_ids = anime['anime_id'].tolist()
tfidf_feature_names, tfidf_matrix = calculate_tfidf_matrix(anime)

watched_ratings = ratings.loc[ratings['rating'] != -1]

# simple popularity recommender (fastest)
print('Popularity recommender: \n')
pr = PopularityRecommender()
print(
    f'Most popular anime overall:\n {pr.give_recommendation(anime, 10)}', '\n'*3)

# popularity by query
print('Popularity by query: \n')
action_or_adventure_anime = filter_by_query('genre', lambda x: bool(
    re.search(r'Action|Adventure', x, re.IGNORECASE)), anime)
print(
    f'Most popular Action / Adventure anime:\n {pr.give_recommendation(action_or_adventure_anime, 10)}', '\n'*3)


# content recommender (slowest)
pb = ProfileBuilder(anime, item_ids, 'user_id', 'anime_id',
                    'rating', watched_ratings, tfidf_matrix)
user_profiles = pb.build_all_user_profiles()
print('Perceived preferences of user 20002: \n')
print(pd.DataFrame(sorted(zip(tfidf_feature_names,
                              user_profiles[20001].flatten().tolist()), key=lambda x: -x[1])[:20],
                   columns=['token', 'relevance']), '\n')

print('Content based recommendations for user 20002: \n')
cr = ContentRecommender(user_profiles, tfidf_matrix, item_ids)
recs = cr.give_recommendation(20002, 'anime_id', anime, verbose=True)
print(recs, '\n'*3)

# collab recommender (most individually accurate)
colr = CollabRecommender(watched_ratings,
                         'user_id', 'anime_id', 'rating')
print('Collab based recommendations for user 20002: \n')
print(colr.give_recommendations(user_id=20002, items_df=anime, verbose=True), '\n'*5)

# hybrid recommender (most accurate)
print('Hybrid recommendations for user 20002: \n')
hr = HybridRecommender(cr, colr, 'anime_id', {'content': 1.0, 'collab': 10.0})
print(hr.give_recommendations(user_id=20002, items_df=anime, topn=10, verbose=True))
