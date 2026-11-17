def rotation_policy(prediction):

    print("\n========== KEY ROTATION POLICY ==========")

    if prediction < 0:

        action = "NORMAL"

        print("Risk Level: NORMAL")

        print("Action: Maintain existing key rotation schedule.")
        return action

    elif prediction <= 1.0:

        action = "ELEVATED"

        print("Risk Level: ELEVATED")

        print("Action: Increase key rotation frequency.")
        return action

    else:

        action = "HIGH"

        print("Risk Level: HIGH")

        print("Action: Request immediate key rotation.")
        return action
