from GlobalVariable import KNN_Model

# PAST_LENGTH = 0


def predict_knn(X, y, current):
    """
    Predict the current area using the KNN model
    :param current:
    :return:
    """
    # global PAST_LENGTH

    print("Before fit")

    # if len(X) != PAST_LENGTH:
    KNN_Model.fit(X, y)
        # PAST_LENGTH = len(X)

    print("After fit")

    result = KNN_Model.predict([current])

    print("After predict")
    return result[0]