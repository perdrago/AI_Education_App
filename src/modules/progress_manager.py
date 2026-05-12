"""
Progress Manager - Manages stars, coins, HP, and lesson completion
"""

import json
import os
from typing import Dict, Optional, Set


class ProgressManager:
    """Manages student progress, stars, coins, and lesson completion."""
    
    def __init__(self, progress_file: str = "game/progress.json"):
        self.progress_file = progress_file
        self.data = self._load_progress()
        
    def _load_progress(self) -> dict:
        """Load progress from JSON file."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Migrate from version 1 to version 2
                    if data.get("version", 1) == 1:
                        print("🔄 Migrating progress from version 1 to version 2...")
                        data = {
                            "version": 2,
                            "total_coins": 0,
                            "lessons": {},
                            "unlocked_examples": [],
                            "permanently_unlocked_functions": []
                        }
                        self._save_progress_data(data)
                    
                    return data
            except:
                pass
        
        # Default structure
        return {
            "version": 2,
            "total_coins": 0,
            "lessons": {},
            "unlocked_examples": [],
            "permanently_unlocked_functions": []
        }
    
    def _save_progress_data(self, data):
        """Save specific progress data to JSON file."""
        os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_progress(self):
        """Save progress to JSON file."""
        self._save_progress_data(self.data)
    
    # ═══════════════════════════════════════════════════════════
    # LESSON PROGRESS
    # ═══════════════════════════════════════════════════════════
    
    def get_lesson_data(self, lesson_id: int) -> dict:
        """Get data for a specific lesson."""
        lesson_key = f"lesson_{lesson_id}"
        if lesson_key not in self.data["lessons"]:
            self.data["lessons"][lesson_key] = {
                "steps": {},
                "challenge_unlocked": False,
                "challenge_completed": False,
                "challenge_hp": 5,
                "total_stars_earned": 0
            }
        return self.data["lessons"][lesson_key]
    
    def get_step_data(self, lesson_id: int, step_num: int) -> dict:
        """Get data for a specific step."""
        lesson_data = self.get_lesson_data(lesson_id)
        step_key = f"step_{step_num}"
        
        if step_key not in lesson_data["steps"]:
            lesson_data["steps"][step_key] = {
                "completed": False,
                "stars_earned": 0,
                "hint_used": False,
                "solution_used": False,
                "attempts": 0
            }
        
        return lesson_data["steps"][step_key]
    
    def complete_step(self, lesson_id: int, step_num: int, hint_used: bool, solution_used: bool):
        """
        Mark a step as completed and award stars.
        
        Returns:
            int: Number of stars earned (0, 1, or 2)
        """
        step_data = self.get_step_data(lesson_id, step_num)
        lesson_data = self.get_lesson_data(lesson_id)
        
        # Calculate stars earned
        if solution_used:
            stars = 0
        elif hint_used:
            stars = 1
        else:
            stars = 2
        
        # Update step data
        step_data["completed"] = True
        step_data["hint_used"] = hint_used
        step_data["solution_used"] = solution_used
        step_data["attempts"] += 1
        
        # Only update stars if this is better than before
        if stars > step_data["stars_earned"]:
            old_stars = step_data["stars_earned"]
            step_data["stars_earned"] = stars
            
            # Update total stars for lesson
            lesson_data["total_stars_earned"] += (stars - old_stars)
        
        # Check if all steps are completed to unlock challenge
        self._check_unlock_challenge(lesson_id)
        
        self._save_progress()
        return stars
    
    def _check_unlock_challenge(self, lesson_id: int):
        """Check if all steps are completed and unlock challenge."""
        lesson_data = self.get_lesson_data(lesson_id)
        
        # Get actual step count from lesson_structure.json
        try:
            import json
            with open("lessons/lesson_structure.json", 'r', encoding='utf-8') as f:
                structure = json.load(f)
                lessons = structure.get("lessons", [])
                
                # Find the lesson
                for lesson in lessons:
                    if lesson.get("id") == lesson_id:
                        total_steps = len(lesson.get("steps", []))
                        break
                else:
                    total_steps = 5  # Default fallback
        except:
            total_steps = 5  # Default fallback
        
        # Count completed steps
        completed_steps = sum(
            1 for step_data in lesson_data["steps"].values()
            if step_data.get("completed", False)
        )
        
        # Unlock challenge if all steps completed
        if completed_steps >= total_steps:
            lesson_data["challenge_unlocked"] = True
            print(f"🔓 Challenge unlocked for Lesson {lesson_id}! ({completed_steps}/{total_steps} steps completed)")
        else:
            print(f"🔒 Challenge locked for Lesson {lesson_id}. ({completed_steps}/{total_steps} steps completed)")
    
    def is_challenge_unlocked(self, lesson_id: int) -> bool:
        """Check if challenge is unlocked for a lesson."""
        lesson_data = self.get_lesson_data(lesson_id)
        return lesson_data.get("challenge_unlocked", False)
    
    def get_total_stars_for_lesson(self, lesson_id: int) -> int:
        """Get total stars earned in a lesson (before challenge)."""
        lesson_data = self.get_lesson_data(lesson_id)
        return lesson_data.get("total_stars_earned", 0)
    
    # ═══════════════════════════════════════════════════════════
    # CHALLENGE & HP
    # ═══════════════════════════════════════════════════════════
    
    def start_challenge(self, lesson_id: int) -> tuple[int, int]:
        """
        Start a challenge. Convert stars to coins and reset HP.
        
        Returns:
            tuple: (stars_earned, coins_added)
        """
        lesson_data = self.get_lesson_data(lesson_id)
        
        # Get stars earned from steps
        stars = lesson_data.get("total_stars_earned", 0)
        
        # Convert stars to coins (1 star = 1 coin)
        coins_added = stars
        self.data["total_coins"] += coins_added
        
        # Reset HP to 5
        lesson_data["challenge_hp"] = 5
        
        self._save_progress()
        return stars, coins_added
    
    def get_challenge_hp(self, lesson_id: int) -> int:
        """Get current HP for challenge."""
        lesson_data = self.get_lesson_data(lesson_id)
        return lesson_data.get("challenge_hp", 5)
    
    def decrease_challenge_hp(self, lesson_id: int) -> int:
        """
        Decrease HP by 1 for wrong answer.
        
        Returns:
            int: Remaining HP
        """
        lesson_data = self.get_lesson_data(lesson_id)
        current_hp = lesson_data.get("challenge_hp", 5)
        new_hp = max(0, current_hp - 1)
        lesson_data["challenge_hp"] = new_hp
        self._save_progress()
        return new_hp
    
    def complete_challenge(self, lesson_id: int) -> Set[str]:
        """
        Mark challenge as completed and permanently unlock functions.
        
        Returns:
            Set[str]: Set of permanently unlocked function IDs
        """
        lesson_data = self.get_lesson_data(lesson_id)
        lesson_data["challenge_completed"] = True
        
        # Get functions to unlock from step_functions.json
        unlocked_functions = self._get_lesson_functions(lesson_id)
        
        # Add to permanently unlocked functions
        for func in unlocked_functions:
            if func not in self.data["permanently_unlocked_functions"]:
                self.data["permanently_unlocked_functions"].append(func)
        
        self._save_progress()
        return set(unlocked_functions)
    
    def _get_lesson_functions(self, lesson_id: int) -> list:
        """Get all functions used in a lesson from step_functions.json."""
        try:
            with open("lessons/step_functions.json", 'r', encoding='utf-8') as f:
                step_functions = json.load(f)
            
            # Collect all unique functions from all steps in this lesson
            functions = set()
            
            # Try nested structure first (lesson_1 -> step_1 -> [functions])
            lesson_key = f"lesson_{lesson_id}"
            if lesson_key in step_functions:
                lesson_data = step_functions[lesson_key]
                for step_key, func_list in lesson_data.items():
                    if isinstance(func_list, list):
                        functions.update(func_list)
            else:
                # Try flat structure (lesson1_step1 -> [functions])
                for step_key, func_list in step_functions.items():
                    if step_key.startswith(f"lesson{lesson_id}_"):
                        functions.update(func_list)
            
            return list(functions)
        except Exception as e:
            print(f"⚠️ Error loading functions for lesson {lesson_id}: {e}")
            return []
    
    def is_challenge_completed(self, lesson_id: int) -> bool:
        """Check if challenge is completed."""
        lesson_data = self.get_lesson_data(lesson_id)
        return lesson_data.get("challenge_completed", False)
    
    def reset_challenge(self, lesson_id: int):
        """Reset challenge HP to retry."""
        lesson_data = self.get_lesson_data(lesson_id)
        lesson_data["challenge_hp"] = 5
        self._save_progress()
    
    # ═══════════════════════════════════════════════════════════
    # COINS & EXAMPLES
    # ═══════════════════════════════════════════════════════════
    
    def get_total_coins(self) -> int:
        """Get total coins available."""
        return self.data.get("total_coins", 0)
    
    def spend_coins(self, amount: int) -> bool:
        """
        Spend coins to unlock an example.
        
        Returns:
            bool: True if successful, False if not enough coins
        """
        current_coins = self.get_total_coins()
        if current_coins >= amount:
            self.data["total_coins"] -= amount
            self._save_progress()
            return True
        return False
    
    def unlock_example(self, example_id: str, cost: int) -> bool:
        """
        Unlock an example by spending coins.
        
        Returns:
            bool: True if successful, False if not enough coins or already unlocked
        """
        if example_id in self.data["unlocked_examples"]:
            return False  # Already unlocked
        
        if self.spend_coins(cost):
            self.data["unlocked_examples"].append(example_id)
            self._save_progress()
            return True
        return False
    
    def is_example_unlocked(self, example_id: str) -> bool:
        """Check if an example is unlocked."""
        return example_id in self.data.get("unlocked_examples", [])
    
    # ═══════════════════════════════════════════════════════════
    # FUNCTION UNLOCKING
    # ═══════════════════════════════════════════════════════════
    
    def get_permanently_unlocked_functions(self) -> Set[str]:
        """Get set of permanently unlocked functions."""
        return set(self.data.get("permanently_unlocked_functions", []))
    
    def is_function_permanently_unlocked(self, func_id: str) -> bool:
        """Check if a function is permanently unlocked."""
        return func_id in self.data.get("permanently_unlocked_functions", [])


# Global instance
_progress_manager = None

def get_progress_manager() -> ProgressManager:
    """Get global progress manager instance."""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    return _progress_manager
