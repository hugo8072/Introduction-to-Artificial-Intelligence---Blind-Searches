import time
from tables import tables


def calculate_possibilities_with_stations(coins):
    """
    Calculate all possible configurations of stations and deputies within a given coin budget.

    Parameters:
    coins (int): The number of coins available.

    Returns:
    list of dict: A list of possible configurations with their respective costs and radii.
    """
    possibilities = []
    sheriff_station_cost = 4
    deputy_costs = [0, 1, 5, 13]  # Possible deputies configurations
    deputy_to_radius = {0: 1, 1: 2, 5: 3, 13: 4}  # Mapping deputies to radii

    max_stations = coins // sheriff_station_cost

    def find_combinations(current_stations, current_coins, station_deputies):
        """
        Helper function to generate unique combinations of deputies.

        Parameters:
        current_stations (int): The number of stations left to place.
        current_coins (int): The number of coins left.
        station_deputies (list of int): The current list of deputies' costs for each station.
        """
        if current_stations == 0:
            total_deputies = sum(station_deputies)
            total_cost = len(station_deputies) * sheriff_station_cost + total_deputies
            if total_cost <= coins:
                possibilities.append({
                    'stations': len(station_deputies),
                    'deputies': total_deputies,
                    'total_cost': total_cost,
                    'remaining_coins': coins - total_cost,
                    'station_radii': [deputy_to_radius[d] for d in station_deputies]
                })
        else:
            last_deputy = station_deputies[-1] if station_deputies else -1
            for cost in deputy_costs:
                if current_coins >= sheriff_station_cost + cost and (not station_deputies or cost >= last_deputy):
                    find_combinations(current_stations - 1, current_coins - (sheriff_station_cost + cost),
                                      station_deputies + [cost])

    for num_stations in range(1, max_stations + 1):
        find_combinations(num_stations, coins, [])

    return possibilities


def dfs_for_family_protection(nxm_map, target_families, station_radii):
    """
    Perform a depth-first search to find the best station placements to protect families.

    Parameters:
    nxm_map (list of list of int): The grid representing the map with family distributions.
    target_families (int): The number of families to protect.
    station_radii (list of int): The radii of the stations.

    Returns:
    tuple: The best solution found, including station positions, total families covered,
     generations, expansions, and time taken.
    """
    generations = 0
    expansions = 0
    start_time = time.time()
    map_height = len(nxm_map)
    map_width = len(nxm_map[0])
    first_gen = False

    if not first_gen:
        print("First generation: Empty map")
        generations = 1

    def dfs_from_point(covered_cells, areas, total_families, depth):
        """
        Recursive helper function for depth-first search.

        Parameters:
        covered_cells (set of tuple of int): The set of cells currently covered by stations.
        areas (list of tuple of int): The list of current station positions.
        total_families (int): The total number of families currently covered.
        depth (int): The current depth of the search.

        Returns:
        tuple: The best solution found at this depth.
        """
        nonlocal generations, expansions
        expansions += 1

        if depth == len(station_radii) or total_families >= target_families:
            return areas, total_families, generations, expansions, time.time() - start_time

        best_solution = (areas, total_families, generations, expansions, time.time() - start_time)
        for i in range(len(nxm_map)):
            for j in range(len(nxm_map[0])):
                generations += 1

                if 0 <= depth - 1 < len(areas):
                    if areas[depth - 1] != (i, j):
                        print("Previous area at depth", depth, ":", areas[depth - 1], "current coordinate", j, i,
                              "generations:", generations, "expansions:", expansions)
                    else:
                        generations -= 1
                else:
                    print("Previous area at depth: None", "current coordinate", j, i, "generations:", generations,
                          "expansions:", expansions)

                radius = station_radii[depth]
                new_covered = {(x, y) for x in range(i - radius, i + radius + 1)
                               for y in range(j - radius, j + radius + 1)
                               if 0 <= x < len(nxm_map) and 0 <= y < len(nxm_map[0])}

                total_families_covered_with_station = total_families + sum(nxm_map[k][l] for k, l in new_covered if
                                                                           (k, l) not in covered_cells and 0 <= k < len(
                                                                               nxm_map) and 0 <= l < len(nxm_map[0]))

                if total_families_covered_with_station >= target_families:
                    return areas + [
                        (i, j)], total_families_covered_with_station, generations, expansions, time.time() - start_time

                if total_families_covered_with_station > best_solution[1]:
                    best_solution = (areas + [(i, j)], total_families_covered_with_station, generations, expansions,
                                     time.time() - start_time)

                if depth + 1 < len(station_radii):
                    next_level_solution = dfs_from_point(covered_cells.union(new_covered), areas + [(i, j)],
                                                         total_families_covered_with_station, depth + 1)

                    if next_level_solution[1] > best_solution[1]:
                        best_solution = next_level_solution

                    if next_level_solution[1] >= target_families:
                        return next_level_solution

                if all(area == (map_height - 1, map_width - 1) for area in
                       areas[-depth:]) and i == map_height - 1 and j == map_width - 1:
                    print("Stop condition reached. All possibilities tested for depth:", depth + 1)
                    if depth == 0:
                        print("Best solution:")

                    return best_solution

        return best_solution

    return dfs_from_point(set(), [], 0, 0)


def print_map_with_stations(nxm_map, station_positions, station_radii):
    """
    Print the map with the given station positions and their respective radii.

    Parameters:
    nxm_map (list of list of int): The grid representing the map with family distributions.
    station_positions (list of tuple of int): The positions of the stations.
    station_radii (list of int): The radii of the stations.
    """
    covered_cells = set()

    for (x, y), radius in zip(station_positions, station_radii):
        for i in range(x - radius, x + radius + 1):
            for j in range(y - radius, y + radius + 1):
                if 0 <= i < len(nxm_map) and 0 <= j < len(nxm_map[0]):
                    covered_cells.add((i, j))

    for i in range(len(nxm_map)):
        for j in range(len(nxm_map[i])):
            cell = nxm_map[i][j]
            if (i, j) in station_positions:
                # If the cell is a station position, add an asterisk without parentheses
                cell_str = f"{cell}*".rjust(4)
            elif (i, j) in covered_cells:
                # If the cell is covered and not a station position, add parentheses
                cell_str = f"({cell})".rjust(4)
            else:
                # If not covered and not a station position, print normally
                cell_str = f"{cell}".rjust(4)
            print(cell_str, end=' ')
        print()  # New line after printing each row of the map


def main():
    """
    Main function to display the menu and handle user input.
    """
    while True:
        print("\nMENU:")
        print("1 - Calculate possibilities for station and deputy distribution")
        print("2 - Choose a map and present a solution")

        choice = input("Choose an option (1/2): ")

        if choice == '1':
            coins = int(input("Enter the number of coins available: "))
            possibilities = calculate_possibilities_with_stations(coins)
            print("\nPossibilities:")
            for possibility in possibilities:
                print(possibility)
        elif choice == '2':
            map_choice = int(input(f"Which map would you like to use (1-{len(tables)}): ")) - 1
            if map_choice < 0 or map_choice >= len(tables):
                print("Invalid choice. Please choose a number between 1 and 10.")
            else:
                coins = int(input("How many coins do you have: "))
                possibilities = calculate_possibilities_with_stations(coins)
                print("Available options based on coins:")
                for idx, option in enumerate(possibilities, start=1):
                    print(
                        f"{idx}. Stations: {option['stations']}, Deputies: {option['deputies']}, "
                        f"Total cost: {option['total_cost']}, Remaining coins: {option['remaining_coins']}")

                option_choice = int(input(f"Choose one of the options (1-{len(possibilities)}): ")) - 1
                if option_choice < 0 or option_choice >= len(possibilities):
                    print("Invalid choice. Please select one of the listed options.")
                else:
                    selected_option = possibilities[option_choice]
                    print(
                        f"You chose the option with {selected_option['stations']} "
                        f"sheriff stations and {selected_option['deputies']} deputies.")
                    print(f"Radius configuration for each station: {selected_option['station_radii']}")
                    target_families = int(input("How many families do you want to protect? "))
                    result = dfs_for_family_protection(tables[map_choice], target_families,
                                                       selected_option['station_radii'])

                    station_positions, total_families_covered, generations, expansions, time = result
                    print("Families protected:", total_families_covered)
                    print_map_with_stations(tables[map_choice], station_positions, selected_option['station_radii'])
                    print("Generations:", generations, "Expansions:", expansions, "Execution time:", time)


if __name__ == "__main__":
    main()
