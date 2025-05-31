mongo_uri = "mongodb://myAdmin:myAdmin@localhost:27017"
db = "vector_search"
collection = "products"
sentence_transformers_image_model_name = "clip-ViT-L-14" # english but much better accuracy than multi lingual model
#sentence_transformers_image_model_name = "sentence-transformers/clip-ViT-B-32" 

sentence_transformers_text_model_name = "clip-ViT-L-14" # english but much better accuracy than multi lingual model
#sentence_transformers_text_model_name = "sentence-transformers/clip-ViT-B-32-multilingual-v1" # multilingual model
number_of_dimensions = 768 # sentence-transformers/clip-ViT-B-32: 512, clip-ViT-L-14: 768 dimensions

# number of worker processes to initialize that each thread encodes images in the folder concurrently
number_of_workers=4
