# Student Name: Rahenvay Arvin Naibaho & Jose Alonso Tiono
# Student ID: 202200177 & 202300181
import os
from pyswip import Prolog

def create_hidden_map():
    return {
        (3, 1): 'W',
        (3, 3): 'P',
        (4, 4): 'P',
        (2, 3): 'G',
        (4, 2): 'G'
    }

def get_percepts(x, y, world_map):
    percepts = []
    neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    for nx, ny in neighbors:
        if 1 <= nx <= 4 and 1 <= ny <= 4:
            if world_map.get((nx, ny)) == 'W':
                if 'Stench' not in percepts: percepts.append('Stench')
            if world_map.get((nx, ny)) == 'P':
                if 'Breeze' not in percepts: percepts.append('Breeze')
    if world_map.get((x, y)) == 'G':
        percepts.append('Glitter')
    return percepts

def generate_post_mission_report(visited, gold_locations, prolog):
    print("\nMission report")
    print("--------------")
    print("[V] visited  [G] gold  [P] pit  [W] wumpus  [?] unknown\n")
    
    for y in range(4, 0, -1):
        row_display = ""
        for x in range(1, 5):
            if (x, y) in visited:
                if (x, y) in gold_locations:
                    row_display += "[G] "
                else:
                    row_display += "[V] "
            else:
                is_not_pit = list(prolog.query(f"not_a_pit({x}, {y})"))
                is_not_wumpus = list(prolog.query(f"not_a_wumpus({x}, {y})"))
                
                if not is_not_pit and not is_not_wumpus:
                    row_display += "[?] " 
                elif not is_not_pit:
                    row_display += "[P] "
                elif not is_not_wumpus:
                    row_display += "[W] "
                else:
                    row_display += "[ ] " 
        print(row_display)
        
    print("\nGold found:")
    if not gold_locations:
        print("None")
    else:
        for idx, loc in enumerate(gold_locations, 1):
            print(f"{idx}. {loc}")
    print()

def main():
    # Force absolute pathing to prevent directory errors
    current_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(current_dir, "wumpus_kb.pl").replace("\\", "/")

    prolog = Prolog()
    prolog.consult(kb_path)
    
    world_map = create_hidden_map()
    
    print("Wumpus World")
    try:
        gold_goal = int(input("Enter the number of gold pieces to find (n): "))
    except ValueError:
        print("Invalid input. Using 1.")
        gold_goal = 1

    current_pos = (1, 1)
    gold_collected = 0
    gold_locations_found = []
    visited_history = set()
    
    prolog.assertz(f"visited(1, 1)")
    visited_history.add((1, 1))

    print("\nStart")
    
    while gold_collected < gold_goal:
        x, y = current_pos
        print(f"\nAt ({x}, {y})")
        
        percepts = get_percepts(x, y, world_map)
        print(f"Percepts: {percepts if percepts else 'none'}")
        
        if 'Breeze' in percepts:
            if not list(prolog.query(f"percept_breeze({x}, {y})")):
                prolog.assertz(f"percept_breeze({x}, {y})")
        if 'Stench' in percepts:
            if not list(prolog.query(f"percept_stench({x}, {y})")):
                prolog.assertz(f"percept_stench({x}, {y})")
            
        if 'Glitter' in percepts and (x, y) not in gold_locations_found:
            print("Gold found.")
            gold_collected += 1
            gold_locations_found.append((x, y))
            world_map[(x, y)] = 'Empty' 
            
        if gold_collected >= gold_goal:
            print("\nGoal reached.")
            break
            
        safe_unvisited_moves = []
        for q_x in range(1, 5):
            for q_y in range(1, 5):
                if (q_x, q_y) not in visited_history:
                    if list(prolog.query(f"is_safe({q_x}, {q_y})")):
                        safe_unvisited_moves.append((q_x, q_y))
                        
        adjacent_safe = [m for m in safe_unvisited_moves if abs(m[0]-x) + abs(m[1]-y) == 1]
        
        if adjacent_safe:
            next_move = adjacent_safe[0]
            print(f"Move to {next_move}")
        else:
            reachable_safe = []
            for sx, sy in safe_unvisited_moves:
                for vx, vy in visited_history:
                    if abs(sx-vx) + abs(sy-vy) == 1:
                        reachable_safe.append((sx, sy))
            
            if reachable_safe:
                next_move = reachable_safe[0]
                print(f"Backtrack to {next_move}")
            else:
                print("\nNo safe move left.")
                break
                
        current_pos = next_move
        visited_history.add(current_pos)
        prolog.assertz(f"visited({current_pos[0]}, {current_pos[1]})")

    generate_post_mission_report(visited_history, gold_locations_found, prolog)

if __name__ == "__main__":
    main()