"""
Function Lock Manager - Manages which functions are locked/unlocked
Simple JSON-based approach for step-by-step unlocking
"""

import json
import os


class FunctionLockManager:
    """
    Manages the lock/unlock state of functions based on lesson completion.
    Uses simple JSON file for step-function mapping.
    """
    
    def __init__(self, progress_file="game/progress.json", step_functions_file="lessons/step_functions.json"):
        self.progress_file = progress_file
        self.step_functions_file = step_functions_file
        self.unlocked_functions = set()
        self.completed_lessons = set()
        self.temporary_unlocked_functions = set()
        self.active_lesson_id = None
        self.active_step_number = 1
        
        # Load step-function mapping from JSON
        self.step_function_map = self._load_step_function_map()
        
        # Load progress from file
        self._load_progress()
    
    def _load_step_function_map(self):
        """Load step-function mapping from JSON file."""
        if os.path.exists(self.step_functions_file):
            try:
                with open(self.step_functions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ Loaded step-function mapping from {self.step_functions_file}")
                    return data
            except Exception as e:
                print(f"⚠️ Error loading step-function mapping: {e}")
                return {}
        else:
            print(f"⚠️ Step-function mapping file not found: {self.step_functions_file}")
            return {}
        
        # Default unlocked categories (always available)
        # Logic Operations and Variables are basic Python commands, always unlocked
        self.default_unlocked_categories = [
            "Logic operations",
            "Variable"
        ]
        
        # Locked categories (require lesson completion)
        self.locked_categories = [
            "Camera",
            "Image Processing",
            "AI Vision core",
            "Display & Dashboard",
            "Robotics"
        ]
        
        # Mapping: lesson_id -> list of functions to unlock
        self.lesson_function_map = {
            "1": [  # Camera Basics
                "Init_Camera",
                "Capture_Image",
                "Display_Image",
                "Save_Image",
                "Load_Image"
            ],
            "2": [  # Image Processing
                "Apply_Blur",
                "Apply_Grayscale",
                "Apply_Edge_Detection",
                "Resize_Image",
                "Rotate_Image"
            ],
            "3": [  # Drawing & Shapes
                "Draw_Rectangle",
                "Draw_Circle",
                "Draw_Line",
                "Draw_Text"
            ]
        }
        
        # Load progress from file
        self._load_progress()
    
    def _load_progress(self):
        """Load progress from JSON file."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_lessons = set(data.get('completed_lessons', []))
                    self.unlocked_functions = set(data.get('unlocked_functions', []))
            except Exception as e:
                print(f"Error loading progress: {e}")
                self.completed_lessons = set()
                self.unlocked_functions = set()
        else:
            self.completed_lessons = set()
            self.unlocked_functions = set()
    
    def _save_progress(self):
        """Save progress to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            data = {
                'completed_lessons': list(self.completed_lessons),
                'unlocked_functions': list(self.unlocked_functions)
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def complete_lesson(self, lesson_id):
        """
        Mark a lesson as completed and unlock its functions.
        
        Args:
            lesson_id: ID of the completed lesson (e.g., "1", "2", "3")
        """
        lesson_id = str(lesson_id)
        
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.add(lesson_id)
            
            # Unlock functions associated with this lesson
            if lesson_id in self.lesson_function_map:
                functions = self.lesson_function_map[lesson_id]
                self.unlocked_functions.update(functions)
                print(f"Lesson {lesson_id} completed! Unlocked functions: {functions}")
            
            self._save_progress()
    
    def is_function_unlocked(self, function_name):
        """
        Check if a function is unlocked.
        Integrates with ProgressManager for permanent unlocks.
        
        Args:
            function_name: Name of the function to check
            
        Returns:
            bool: True if unlocked (permanently or temporarily), False if locked
        """
        # Check permanent unlocks from ProgressManager
        try:
            from src.modules.progress_manager import get_progress_manager
            pm = get_progress_manager()
            if pm.is_function_permanently_unlocked(function_name):
                return True
        except:
            # Fallback to old system
            if function_name in self.unlocked_functions:
                return True
        
        # Check temporary unlocks (for active lesson)
        if function_name in self.temporary_unlocked_functions:
            return True
        
        return False
    
    def start_lesson(self, lesson_id, step_number=1, lang="en"):
        """
        Start a lesson step and temporarily unlock its functions.
        Simple approach: just read from JSON file.
        
        Args:
            lesson_id: ID of the lesson being started (e.g., "1", "2", "3")
            step_number: Step number within the lesson (default: 1)
            lang: Language code (not used in simple approach)
        """
        lesson_id = str(lesson_id)
        self.active_lesson_id = lesson_id
        self.active_step_number = step_number
        
        # Get functions from JSON mapping
        lesson_key = f"lesson_{lesson_id}"
        step_key = f"step_{step_number}"
        
        step_functions = []
        if lesson_key in self.step_function_map:
            step_functions = self.step_function_map[lesson_key].get(step_key, [])
        
        # Temporarily unlock functions for this step
        if step_functions:
            self.temporary_unlocked_functions = set(step_functions)
            print(f"🔓 Lesson {lesson_id} Step {step_number}: Unlocked {len(step_functions)} functions")
            print(f"   Functions: {', '.join(step_functions)}")
        else:
            self.temporary_unlocked_functions = set()
            print(f"⚠️ No functions defined for Lesson {lesson_id} Step {step_number}")
    
    def update_step(self, step_number, lang="en"):
        """
        Update to a new step within the current lesson.
        
        Args:
            step_number: New step number
            lang: Language code (not used)
        """
        if not self.active_lesson_id:
            print("⚠️ No active lesson to update step")
            return
        
        self.active_step_number = step_number
        
        # Get functions from JSON mapping
        lesson_key = f"lesson_{self.active_lesson_id}"
        step_key = f"step_{step_number}"
        
        step_functions = []
        if lesson_key in self.step_function_map:
            step_functions = self.step_function_map[lesson_key].get(step_key, [])
        
        # Update temporary unlocks
        if step_functions:
            self.temporary_unlocked_functions = set(step_functions)
            print(f"🔄 Step {step_number}: Unlocked {len(step_functions)} functions")
            print(f"   Functions: {', '.join(step_functions)}")
        else:
            self.temporary_unlocked_functions = set()
            print(f"⚠️ No functions defined for Step {step_number}")
    
    def end_lesson(self, lesson_id, completed=False):
        """
        End a lesson and remove temporary unlocks (unless completed).
        
        Args:
            lesson_id: ID of the lesson being ended
            completed: Whether the lesson was completed successfully
        """
        lesson_id = str(lesson_id)
        
        if completed:
            # Lesson completed - make unlocks permanent
            self.complete_lesson(lesson_id)
        else:
            # Lesson not completed - remove temporary unlocks
            print(f"Lesson {lesson_id} ended without completion. Removing temporary unlocks.")
            self.temporary_unlocked_functions = set()
        
        self.active_lesson_id = None
    
    def get_all_unlocked_functions(self):
        """
        Get all unlocked functions (permanent + temporary).
        Integrates with ProgressManager for permanent unlocks.
        
        Returns:
            set: Combined set of permanently and temporarily unlocked functions
        """
        # Get permanent unlocks from ProgressManager
        permanent_unlocks = set()
        try:
            from src.modules.progress_manager import get_progress_manager
            pm = get_progress_manager()
            permanent_unlocks = pm.get_permanently_unlocked_functions()
        except:
            # Fallback to old system
            permanent_unlocks = self.unlocked_functions
        
        # Combine with temporary unlocks
        return permanent_unlocks | self.temporary_unlocked_functions
    
    def is_category_unlocked(self, category_name):
        """
        Check if a category is unlocked (has at least one unlocked function).
        
        Args:
            category_name: Name of the category
            
        Returns:
            bool: True if category is default unlocked or has unlocked functions
        """
        # Default unlocked categories are always available
        if category_name in self.default_unlocked_categories:
            return True
        
        # Check if category is in locked list
        if category_name in self.locked_categories:
            # Check if any function in this category is unlocked
            # This would require mapping functions to categories
            # For now, return False if no lessons completed
            return len(self.completed_lessons) > 0
        
        return True
    
    def get_unlocked_functions(self):
        """Get set of all unlocked functions."""
        return self.unlocked_functions.copy()
    
    def get_completed_lessons(self):
        """Get set of all completed lessons."""
        return self.completed_lessons.copy()
    
    def reset_progress(self):
        """Reset all progress (for testing/debugging)."""
        self.completed_lessons = set()
        self.unlocked_functions = set()
        self._save_progress()
        print("Progress reset!")
    
    def get_functions_for_lesson(self, lesson_id):
        """Get list of functions that will be unlocked by completing a lesson."""
        lesson_id = str(lesson_id)
        return self.lesson_function_map.get(lesson_id, [])
