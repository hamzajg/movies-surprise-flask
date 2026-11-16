# explained-recommendations — specifications by example
# Scenario tags @w<N> map items to delivery waves (see WAVES.md / BACKLOG.md).

Feature: explained-recommendations

  @w1 @happy-path
  Scenario: Explained recs cite rated neighbors
    Given a user who rated movies similar to a recommended movie
    When the explanation for that recommendation is built
    Then its reasons list similar movies the user rated, each with similarity and userRating

  @w1
  Scenario: Reasons use model-user ratings
    Given a rating map built from a trainset
    When reasons are requested for a movie
    Then only movies present in that user's ratings appear as reasons

  @w1
  Scenario: No rated neighbors is not an error
    Given a user with no ratings overlapping a movie's neighbors
    When reasons are requested
    Then the result is an empty list

  @w2 @happy-path
  Scenario: Response keeps score contract
    Given a valid /score-shaped request with explainLimit
    When a client POSTs /explain-recs
    Then the response contains movieIds and predictedRatings like /score
    And explanations carries reasons per movieId

  @w2
  Scenario: Validation matches score
    Given a missing or malformed JSON body
    When a client POSTs /explain-recs
    Then the response is 400 like /score
