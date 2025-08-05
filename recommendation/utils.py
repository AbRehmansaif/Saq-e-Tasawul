# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import linear_kernel
# from surprise import Dataset, Reader, SVD
# from surprise.model_selection import train_test_split
# from core.models import Product, ProductReview
# from django.db.models import Q

# # ---- Content-Based Filtering ----
# def get_content_based_recommendations(product_id, top_n=5):
#     products = Product.objects.all()
#     df = pd.DataFrame(list(products.values('id', 'title', 'description', 'category__title')))
#     df['description'] = df['description'].fillna('')
#     df['category__title'] = df['category__title'].fillna('')
    
#     df['combined'] = df['title'] + " " + df['description'] + " " + df['category__title']
    
#     tfidf = TfidfVectorizer(stop_words='english')
#     tfidf_matrix = tfidf.fit_transform(df['combined'])
    
#     cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
#     idx = df.index[df['id'] == product_id][0]
#     sim_scores = list(enumerate(cosine_sim[idx]))
    
#     # Sort by similarity and exclude itself
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = [s for s in sim_scores if df['id'][s[0]] != product_id]
    
#     similar_product_ids = [df['id'][i[0]] for i in sim_scores[:top_n]]
#     return list(Product.objects.filter(id__in=similar_product_ids))


# # ---- Collaborative Filtering ----
# def train_collaborative_model():
#     reviews = ProductReview.objects.exclude(rating=None)
#     if not reviews.exists():
#         return None

#     data = pd.DataFrame(list(reviews.values('user_id', 'product_id', 'rating')))
#     reader = Reader(rating_scale=(1, 5))
#     dataset = Dataset.load_from_df(data[['user_id', 'product_id', 'rating']], reader)

#     trainset, _ = train_test_split(dataset, test_size=0.2)
#     algo = SVD()
#     algo.fit(trainset)
#     return algo

# def get_collaborative_recommendations(user_id, algo, top_n=5):
#     products = Product.objects.all()
#     predictions = [
#         (product.id, algo.predict(user_id, product.id).est)
#         for product in products
#     ]
    
#     # Filter out low-confidence predictions
#     predictions = [(pid, score) for pid, score in predictions if score >= 3.0]
#     predictions.sort(key=lambda x: x[1], reverse=True)
    
#     recommended_ids = [pid for pid, _ in predictions[:top_n]]
#     return list(Product.objects.filter(id__in=recommended_ids))

# import logging
# logger = logging.getLogger(__name__)

# def get_hybrid_recommendations(user_id, product_id, top_n=5):
#     logger.info("🔍 Running Hybrid Recommendation for User %s, Product %s", user_id, product_id)

#     algo = train_collaborative_model()

#     content_recs = get_content_based_recommendations(product_id, top_n)
#     logger.info("📄 Content-based returned: %s", [p.id for p in content_recs])

#     collab_recs = get_collaborative_recommendations(user_id, algo, top_n) if algo else []
#     logger.info("🤝 Collaborative returned: %s", [p.id for p in collab_recs])

#     combined = {p.id: p for p in (content_recs + collab_recs)}
#     final_recommendations = list(combined.values())[:top_n]
#     logger.info("✅ Final Hybrid Recommendations: %s", [p.id for p in final_recommendations])

#     return final_recommendations


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from core.models import Product, ProductReview, wishlist_model
from django.db.models import Q

# ----------------- Content-Based Recommendation -----------------
def get_content_based_recommendations(product_id, top_n=5):
    products = Product.objects.all()
    df = pd.DataFrame(list(products.values('id', 'title', 'description', 'category__title')))
    df['description'] = df['description'].fillna('')
    df['category__title'] = df['category__title'].fillna('')
    
    # Combine features for better similarity
    df['combined'] = df['title'] + " " + df['description'] + " " + df['category__title']
    
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined'])
    
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    idx = df.index[df['id'] == product_id][0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    similar_product_ids = [df['id'][i[0]] for i in sim_scores[1:top_n+1]]
    return list(Product.objects.filter(id__in=similar_product_ids))

# ----------------- Collaborative Filtering with Wishlist -----------------
def train_collaborative_model():
    reviews = ProductReview.objects.exclude(rating=None)
    wishlist = wishlist_model.objects.all()

    # Combine reviews and wishlist into a single dataset
    review_data = pd.DataFrame(list(reviews.values('user_id', 'product_id', 'rating')))
    wishlist_data = pd.DataFrame(list(wishlist.values('user_id', 'product_id')))
    
    if not review_data.empty:
        combined_data = review_data
    else:
        combined_data = pd.DataFrame(columns=['user_id', 'product_id', 'rating'])

    if not wishlist_data.empty:
        wishlist_data['rating'] = 5  # Implicit positive feedback
        combined_data = pd.concat([combined_data, wishlist_data], ignore_index=True)

    if combined_data.empty:
        return None

    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(combined_data[['user_id', 'product_id', 'rating']], reader)
    
    trainset, _ = train_test_split(dataset, test_size=0.2)
    algo = SVD()
    algo.fit(trainset)
    
    return algo

def get_collaborative_recommendations(user_id, algo, top_n=5):
    products = Product.objects.all()
    predictions = [
        (product.id, algo.predict(user_id, product.id).est)
        for product in products
    ]
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    recommended_ids = [pid for pid, _ in predictions[:top_n]]
    return list(Product.objects.filter(id__in=recommended_ids))

# ----------------- Hybrid Recommendation -----------------
def get_hybrid_recommendations(user_id, product_id, top_n=5):
    algo = train_collaborative_model()
    
    content_recs = get_content_based_recommendations(product_id, top_n)
    collab_recs = get_collaborative_recommendations(user_id, algo, top_n) if algo else []
    
    # Merge results without duplicates
    combined = {p.id: p for p in (content_recs + collab_recs)}
    
    # Exclude the current product
    final_recommendations = [p for p in combined.values() if p.id != product_id]
    
    return final_recommendations[:top_n]
