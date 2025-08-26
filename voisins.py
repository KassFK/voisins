#!/usr/bin/env python3
"""
Roulette Voisins Tracker

This program tracks roulette numbers and counts how many rounds have passed
without hitting a "voisins du zéro" (neighbors of zero) number.

Voisins du zéro numbers: 22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25
"""

class RouletteVoisinsTracker:
    def __init__(self):
        # Voisins du zéro numbers (neighbors of zero in European roulette)
        self.voisins_numbers = {22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25}
        self.rounds_without_voisins = 0
        self.total_rounds = 0
        self.history = []
        
    def is_voisins(self, number):
        """Check if a number is a voisins number"""
        return number in self.voisins_numbers
    
    def add_number(self, number):
        """Add a new roulette number and update counters"""
        if not (0 <= number <= 36):
            raise ValueError("Roulette number must be between 0 and 36")
        
        self.history.append(number)
        self.total_rounds += 1
        
        if self.is_voisins(number):
            self.rounds_without_voisins = 0
            return True  # Hit a voisins number
        else:
            self.rounds_without_voisins += 1
            return False  # Not a voisins number
    
    def get_status(self):
        """Get current status"""
        return {
            'rounds_without_voisins': self.rounds_without_voisins,
            'total_rounds': self.total_rounds,
            'last_number': self.history[-1] if self.history else None,
            'last_voisins_hit': self.get_last_voisins_number()
        }
    
    def get_last_voisins_number(self):
        """Get the last voisins number that was hit"""
        for number in reversed(self.history):
            if self.is_voisins(number):
                return number
        return None
    
    def display_voisins_numbers(self):
        """Display all voisins numbers"""
        sorted_voisins = sorted(self.voisins_numbers)
        return f"Voisins du zéro numbers: {', '.join(map(str, sorted_voisins))}"
    
    def reset(self):
        """Reset the tracker"""
        self.rounds_without_voisins = 0
        self.total_rounds = 0
        self.history = []

def main():
    tracker = RouletteVoisinsTracker()
    
    print("🎰 Roulette Voisins Tracker")
    print("=" * 50)
    print(tracker.display_voisins_numbers())
    print("=" * 50)
    print("Enter roulette numbers (0-36) or 'q' to quit, 'r' to reset, 's' for status")
    print()
    
    while True:
        try:
            user_input = input("Enter roulette number: ").strip().lower()
            
            if user_input == 'q':
                print("Thanks for using Roulette Voisins Tracker!")
                break
            elif user_input == 'r':
                tracker.reset()
                print("✅ Tracker reset!")
                continue
            elif user_input == 's':
                status = tracker.get_status()
                print(f"\n📊 Current Status:")
                print(f"   Total rounds: {status['total_rounds']}")
                print(f"   Rounds without voisins: {status['rounds_without_voisins']}")
                print(f"   Last number: {status['last_number']}")
                print(f"   Last voisins hit: {status['last_voisins_hit']}")
                print()
                continue
            elif user_input == 'h':
                print(tracker.display_voisins_numbers())
                continue
            
            # Try to convert to number
            number = int(user_input)
            
            # Add the number and get result
            is_voisins_hit = tracker.add_number(number)
            
            if is_voisins_hit:
                print(f"🎯 Number {number} is a VOISINS! Counter reset to 0.")
            else:
                status = tracker.get_status()
                print(f"❌ Number {number} is NOT a voisins. Rounds without voisins: {status['rounds_without_voisins']}")
            
            print()
            
        except ValueError as e:
            if "invalid literal" in str(e):
                print("❗ Please enter a valid number (0-36) or command (q/r/s/h)")
            else:
                print(f"❗ {e}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
