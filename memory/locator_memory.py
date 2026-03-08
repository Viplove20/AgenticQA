def search_locator_fix(locator):

    query = f"locator {locator}"

    embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=1
    )

    if results["documents"]:

        stored = results["documents"][0][0]

        if "->" in stored:
            return stored.split("->")[1].strip()

    return None