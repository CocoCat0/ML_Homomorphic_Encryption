import tenseal as ts


def decrypt_prediction(device_context, encrypted_result):

    encrypted_score = ts.ckks_vector_from(
        device_context,
        encrypted_result
    )

    prediction = encrypted_score.decrypt()[0]

    return prediction

