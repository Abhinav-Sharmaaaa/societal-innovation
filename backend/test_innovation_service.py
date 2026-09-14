from app.ai.innovation_service import predict_innovation


def main() -> None:
    examples = [
        (
            "Routine administrative service delivery "
            "is required to update records and improve "
            "standard follow-up."
        ),
        (
            "The city needs an AI-powered early warning "
            "system using sensors and real-time monitoring "
            "to predict infrastructure failures."
        ),
        (
            "Researchers need to develop a novel "
            "remote sensing system and validate a prototype "
            "for flood prediction."
        ),
    ]

    for index, text in enumerate(
        examples,
        start=1,
    ):
        print("\n" + "=" * 80)
        print(f"EXAMPLE {index}")
        print("=" * 80)

        result = predict_innovation(text)

        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()