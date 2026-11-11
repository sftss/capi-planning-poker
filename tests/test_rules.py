"""Tests : une ligne de la table de décision (rendus/R2.md) par test"""

from capi.rules import Decision, MedianRule, StrictRule, evaluate


def test_CA_02_2_strict_tour1_unanimite_validee():
    # Préparer
    votes = ["5", "5", "5"]
    # Agir
    decision = evaluate(votes, StrictRule(), 1)
    # Vérifier
    assert decision == Decision(validated=True, value="5")


def test_CA_02_1_strict_tour1_un_vote_different_revote():
    # Un seul vote différent casse l'unanimité
    # Préparer
    votes = ["5", "5", "5", "5", "3"]
    # Agir
    decision = evaluate(votes, StrictRule(), 1)
    # Vérifier
    assert decision == Decision(validated=False)


def test_CA_02_3_strict_tour2_reste_unanimite():
    # Préparer
    votes = ["5", "5", "8"]
    # Agir
    decision = evaluate(votes, StrictRule(), 2)
    # Vérifier
    assert decision == Decision(validated=False)


def test_CA_04_1_mediane_tour1_unanimite_exigee():
    # Au premier tour la médiane donnerait 5, mais toutes les règles se joue à l'unanimité
    # Préparer
    votes = ["5", "5", "8"]
    # Agir
    decision = evaluate(votes, MedianRule(), 1)
    # Vérifier
    assert decision == Decision(validated=False)


def test_CA_03_1_mediane_tour2_majorite_nette():
    # Préparer
    votes = ["5", "5", "8"]
    # Agir
    decision = evaluate(votes, MedianRule(), 2)
    # Vérifier
    assert decision == Decision(validated=True, value="5")


def test_CA_03_2_mediane_nombre_pair_carte_superieure():
    # La moyenne des deux valeurs (4) n'est pas une carte, on retient la carte supérieure
    # Préparer
    votes = ["3", "5"]
    # Agir
    decision = evaluate(votes, MedianRule(), 2)
    # Vérifier
    assert decision == Decision(validated=True, value="5")


def test_CA_03_3_mediane_egalite_carte_superieure():
    # Préparer
    votes = ["3", "3", "8", "8"]
    # Agir
    decision = evaluate(votes, MedianRule(), 2)
    # Vérifier
    assert decision == Decision(validated=True, value="8")


def test_CA_03_4_mediane_carte_interrogation_revote():
    # Préparer
    votes = ["5", "8", "?"]
    # Agir
    decision = evaluate(votes, MedianRule(), 2)
    # Vérifier
    assert decision == Decision(validated=False)
