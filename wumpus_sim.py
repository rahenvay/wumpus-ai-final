# Student Name: Rahenvay Arvin Naibaho & Jose Alonso Tiono
# Student ID: 202200177 & 202300181
from pyswip import Prolog

def create_hidden_map():
    """Encodes the 4x4 physical world with Hazards and Gold."""
    # Example Layout: Wumpus at (3,1), Pits at (3,3) & (4,4), Gold at (2,3) & (4,2)
    return {
        (3, 1): 'W',
        (3, 3): 'P',
        (4, 4): 'P',
        (2, 3): 'G',
        (4, 2): 'G'
    }

def get_percepts(x, y, world_map):
    """SENSE: Checks the hidden map for adjacent hazards to generate percepts."""
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
    """Generates the visual 4x4 grid and gold summary."""
    print("\n" + "="*30)
    print("      POST-MISSION REPORT")
    print("="*30)
    print("Legend: [V] Visited  [G] Gold  [P] Possible Pit  [W] Possible Wumpus  [?] Unknown\n")
    
    # Print Grid from top (Y=4) to bottom (Y=1)
    for y in range(4, 0, -1):
        row_display = ""
        for x in range(1, 5):
            if (x, y) in visited:
                if (x, y) in gold_locations:
                    row_display += "[G] "
                else:
                    row_display += "[V] "
            else:
                # ASK Prolog what it thinks about this unvisited square
                is_not_pit = list(prolog.query(f"not_a_pit({x}, {y})"))
                is_not_wumpus = list(prolog.query(f"not_a_wumpus({x}, {y})"))
                
                if not is_not_pit and not is_not_wumpus:
                    row_display += "[?] " # Could be either
                elif not is_not_pit:
                    row_display += "[P] "
                elif not is_not_wumpus:
                    row_display += "[W] "
                else:
                    row_display += "[ ] " # Proven safe, but unvisited
                    
        print(row_display)
        
    print("\n--- Treasure Recovery Summary ---")
    if not gold_locations:
        print("No gold was recovered during this mission.")
    else:
        for idx, loc in enumerate(gold_locations, 1):
            print(f"Piece {idx} recovered at coordinates: {loc}")
    print("=================================\n")

def main():
    # Initialize connection to the "Brain"
    prolog = Prolog()
    prolog.consult("wumpus_kb.pl")
    
    world_map = create_hidden_map()
    
    print("Welcome to the Wumpus World AI Simulator!")
    try:
        gold_goal = int(input("Enter the number of gold pieces to find (n): "))
    except ValueError:
        print("Invalid input. Defaulting to n = 1.")
        gold_goal = 1

    current_pos = (1, 1)
    gold_collected = 0
    gold_locations_found = []
    visited_history = set()
    
    # Initialize the starting square as safe in Prolog
    prolog.assertz(f"visited(1, 1)")
    visited_history.add((1, 1))

    print("\n>>> MISSION START <<<")
    
    # THE MAIN LOOP
    while gold_collected < gold_goal:
        x, y = current_pos
        print(f"\n--- Agent is currently at ({x}, {y}) ---")
        
        # 1. SENSE
        percepts = get_percepts(x, y, world_map)
        print(f"Sensors detect: {percepts if percepts else 'Nothing'}")
        
        # 2. TELL
        if 'Breeze' in percepts:
            # Check if already asserted to avoid duplicates in KB
            if not list(prolog.query(f"percept_breeze({x}, {y})")):
                prolog.assertz(f"percept_breeze({x}, {y})")
        if 'Stench' in percepts:
            if not list(prolog.query(f"percept_stench({x}, {y})")):
                prolog.assertz(f"percept_stench({x}, {y})")
            
        # 3. COLLECT
        if 'Glitter' in percepts and (x, y) not in gold_locations_found:
            print("✨ GOLD RECOVERED! ✨")
            gold_collected += 1
            gold_locations_found.append((x, y))
            world_map[(x, y)] = 'Empty' # Remove gold so we don't count it twice
            
        if gold_collected >= gold_goal:
            print("\n✅ MISSION ACCOMPLISHED! Target gold recovered.")
            break
            
        # 4. REASON & ASK
        safe_unvisited_moves = []
        for q_x in range(1, 5):
            for q_y in range(1, 5):
                if (q_x, q_y) not in visited_history:
                    # Query Prolog to see if the square is proven safe
                    if list(prolog.query(f"is_safe({q_x}, {q_y})")):
                        safe_unvisited_moves.append((q_x, q_y))
                        
        # Filter safe moves to those immediately adjacent to our current position
        adjacent_safe = [m for m in safe_unvisited_moves if abs(m[0]-x) + abs(m[1]-y) == 1]
        
        # 5. ACT
        if adjacent_safe:
            # Move to the first available adjacent safe square
            next_move = adjacent_safe[0]
            print(f"Logic dictates moving to adjacent safe square: {next_move}")
        else:
            # Backtrack: If stuck, find a safe unvisited square attached to ANY previously visited square
            reachable_safe = []
            for sx, sy in safe_unvisited_moves:
                for vx, vy in visited_history:
                    if abs(sx-vx) + abs(sy-vy) == 1:
                        reachable_safe.append((sx, sy))
            
            if reachable_safe:
                next_move = reachable_safe[0]
                print(f"Path blocked. Agent backtracks and moves to known safe square: {next_move}")
            else:
                print("\n🛑 MISSION ABORTED! The agent cannot logically prove any remaining safe moves.")
                break
                
        # Update State for next loop iteration
        current_pos = next_move
        visited_history.add(current_pos)
        prolog.assertz(f"visited({current_pos[0]}, {current_pos[1]})") # TELL KB about the move

    # 6. TERMINATE & REPORT
    generate_post_mission_report(visited_history, gold_locations_found, prolog)

if __name__ == "__main__":
    main()