% Student Name: Rahenvay Arvin Naibaho & Jose Alonso Tiono 
% Student ID: 202200177 & 202300181

% Declare dynamic predicates so Python can update the KB at runtime
:- dynamic visited/2.
:- dynamic percept_breeze/2.
:- dynamic percept_stench/2.

% Define the boundaries of the 4x4 grid
valid_pos(X, Y) :- X >= 1, X =< 4, Y >= 1, Y =< 4.

% Define Adjacency (Up, Down, Left, Right)
adjacent(X1, Y1, X2, Y2) :-
    ( (X2 is X1 + 1, Y2 is Y1);
      (X2 is X1 - 1, Y2 is Y1);
      (X2 is X1, Y2 is Y1 + 1);
      (X2 is X1, Y2 is Y1 - 1) ),
    valid_pos(X1, Y1),
    valid_pos(X2, Y2).


% Inferential Rule: Is there a Pit?
not_a_pit(X, Y) :-
    adjacent(X, Y, AX, AY),
    visited(AX, AY),
    \+ percept_breeze(AX, AY).

% Inferential Rule: Is there a Wumpus?
not_a_wumpus(X, Y) :-
    adjacent(X, Y, AX, AY),
    visited(AX, AY),
    \+ percept_stench(AX, AY).

% Safety Rules
is_safe(X, Y) :- visited(X, Y).

is_safe(X, Y) :-
    valid_pos(X, Y),
    \+ visited(X, Y),
    not_a_pit(X, Y),
    not_a_wumpus(X, Y).