from sentence_transformers import SentenceTransformer, util
from transformers import AutoImageProcessor
from PIL import Image
import pymongo, os, sys
import concurrent.futures
import random

sys.path.insert(1, '../config/')
from config import mongo_uri, db, collection, sentence_transformers_image_model_name, number_of_workers, number_of_dimensions

directoryThatIncludesImages = (sys.argv[1])
NUM_OF_WORKERS = number_of_workers

# initialize db connection
connection = pymongo.MongoClient(mongo_uri)
product_collection = connection[db][collection]



def drop_collection():
    product_collection.drop() # make sure the target collection is empty
    

def create_vector_search_index():
    print("Vector index creation triggered.")
    operation = connection[db].create_collection(collection)

    index_definition = {
    "fields": [
        {
        "type": "vector",
        "path": "imageVector",
        "numDimensions": number_of_dimensions,
        "similarity": "cosine"
        },
        {
        "type": "filter",
        "path": "price"
        },
        {
        "type": "filter",
        "path": "averageRating"
        },
        {
        "type": "filter",
        "path": "discountPercentage"
        }
    ]
    }
    sim = pymongo.operations.SearchIndexModel(type="vectorSearch", name="vector_index", definition=index_definition)
    product_collection.create_search_index(sim)
    message = {"message": "Vector index is being created..."}
    return message


def vectorize(imageFiles,threadNo):
    number_of_files_processed = 0
    for f in imageFiles:
        if os.path.isfile(f):
            encoded = model.encode(Image.open(f)).tolist()
            image = {
                "imageFile": f,
                "imageVector": encoded,
                "price": round(random.uniform(5.0, 100.0),2),
                "discountPercentage" : random.randint(5,25),
                "averageRating": round(random.uniform(3.0, 5.0),2),
            }
            product_collection.insert_one(image)
            number_of_files_processed = number_of_files_processed + 1
            remaining_number_of_files = len(imageFiles) - number_of_files_processed
            print(f"[Thread no: {threadNo}][{remaining_number_of_files} files left] Image has been embedded as a vector in the document:{f}")
        
    return f"Thread number {threadNo} completed, {len(imageFiles)} files have been loaded"


# Multiprocessing version for encoding thousands of image files
from multiprocessing import Pool, cpu_count
def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]

def init_worker(model_path):
    global model
    print(f"model path: {model_path}")
    model = SentenceTransformer(model_path)


if __name__ == "__main__":
    drop_collection()
    create_vector_search_index()

    files = [] 
    for filename in os.listdir(directoryThatIncludesImages):
        f = os.path.join(directoryThatIncludesImages, filename)
        files.append(f)

    
    images_length = len(files)
    number_of_processes = min(NUM_OF_WORKERS, cpu_count())
    image_chunks = chunkify(files, number_of_processes)



    print(f"Number of processes: {number_of_processes}")
    preTrainedModelName = sentence_transformers_image_model_name
    #Load CLIP model, it will take sometime to cache the model
    model = SentenceTransformer(preTrainedModelName)

    pool = Pool(processes=number_of_processes, initializer=init_worker, initargs=(preTrainedModelName,))
    try:
        args = [(chunk, idx + 1) for idx, chunk in enumerate(image_chunks)]
        results = pool.starmap(vectorize, args)
        for result in results:
            print(f"Result: {result}")
    finally:
        pool.close()
        pool.join()
    print("All worker processes have completed. Exiting main process.")

