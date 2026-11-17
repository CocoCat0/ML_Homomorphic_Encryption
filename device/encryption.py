import tenseal as ts


def create_encryption_context(poly_modulus_degree=8192):

    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=poly_modulus_degree,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )

    context.global_scale = 2**40

    context.generate_galois_keys()

    print(f"CKKS encryption context created!")
    print(f"Polynomial modulus degree: {poly_modulus_degree}")

    return context


def encrypt_telemetry(context, telemetry):

    encrypted_data = ts.ckks_vector(
        context,
        telemetry.tolist()
    )

    return encrypted_data


def create_public_context(device_context):

    public_context_bytes = device_context.serialize(
        save_secret_key=False
    )

    return public_context_bytes

