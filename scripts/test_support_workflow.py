from uuid import uuid4

from youcode_ai.orchestration import (
    YouCodeOrchestrationService,
)


def print_response(
    visitor_message: str,
    response,
) -> None:
    print()
    print(
        "Visiteur :",
        visitor_message,
    )

    print(
        "Support :",
        response.answer,
    )

    print(
        response.model_dump_json(
            indent=2
        )
    )


def main() -> None:
    service = (
        YouCodeOrchestrationService()
    )

    identifier = uuid4().hex[:8]

    session_id = (
        f"alternative-test-{identifier}"
    )

    email = (
        f"candidate+{identifier}"
        "@example.com"
    )

    print(
        "Test complet du report de test"
    )

    print("=" * 60)

    # Étape 1 :
    # le visiteur donne toutes les données.
    first_message = (
        "Je souhaite reporter mon test "
        "prévu le 02/08/2026 au campus "
        "de Safi. Je voudrais le passer "
        "à partir du 10/08/2026 car je "
        "ne serai pas disponible à la "
        "date actuelle. Mon adresse "
        f"email est {email}."
    )

    first_response = service.invoke(
        message=first_message,
        session_id=session_id,
    )

    print_response(
        first_message,
        first_response,
    )

    assert (
        first_response.status
        == "awaiting_consent"
    )

    # Étape 2 :
    # le visiteur donne son consentement.
    consent_message = (
        "Oui, je confirme."
    )

    proposal_response = service.invoke(
        message=consent_message,
        session_id=session_id,
    )

    print_response(
        consent_message,
        proposal_response,
    )

    assert (
        proposal_response.status
        == "awaiting_session_confirmation"
    )

    assert (
        proposal_response
        .request_reference
        is not None
    )

    assert (
        proposal_response
        .proposed_test_date
        is not None
    )

    first_proposed_date = (
        proposal_response
        .proposed_test_date
    )

    request_reference = (
        proposal_response
        .request_reference
    )

    # Étape 3 :
    # le visiteur refuse la première date.
    rejection_message = (
        "Non, cette date ne me convient "
        "pas. Je souhaite une autre date."
    )

    alternative_response = (
        service.invoke(
            message=rejection_message,
            session_id=session_id,
        )
    )

    print_response(
        rejection_message,
        alternative_response,
    )

    assert (
        alternative_response.status
        == "awaiting_session_confirmation"
    )

    assert (
        alternative_response
        .request_reference
        == request_reference
    )

    assert (
        alternative_response
        .proposed_test_date
        is not None
    )

    second_proposed_date = (
        alternative_response
        .proposed_test_date
    )

    assert (
        second_proposed_date
        != first_proposed_date
    )

    # Étape 4 :
    # le visiteur accepte la deuxième date.
    acceptance_message = (
        "Oui, cette nouvelle date "
        "me convient."
    )

    final_response = service.invoke(
        message=acceptance_message,
        session_id=session_id,
    )

    print_response(
        acceptance_message,
        final_response,
    )

    assert (
        final_response.status
        == "proposed"
    )

    assert (
        final_response
        .request_reference
        == request_reference
    )

    assert (
        final_response
        .proposed_test_date
        == second_proposed_date
    )

    assert (
        final_response.requires_human
        is True
    )

    print()
    print("=" * 60)

    print(
        "Test terminé avec succès."
    )

    print(
        "Première proposition :",
        first_proposed_date,
    )

    print(
        "Deuxième proposition :",
        second_proposed_date,
    )

    print(
        "Référence :",
        request_reference,
    )


if __name__ == "__main__":
    main()