from typing import List, Optional
from ..models.user import User
from ..core.init_db import get_database
from ..schemas.user_schema import UserCreate, screeningUpdate, GDUpdate, PIUpdate, TaskUpdate, ShortlistRequest, TaskStatusUpdate
from ..models.user import AttendanceUpdate, BulkSlotAssignment
from odmantic import ObjectId

class UserService:
    @staticmethod
    def get_engine():
        """Get the ODMantic engine instance."""
        return get_database()
    """Service for handling user operations"""
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """Convert email to lowercase and strip spaces"""
        return email.strip().lower()

    @staticmethod
    async def create_user(user: UserCreate) -> User:
        """Create a new user in the database"""
        engine = get_database()

        # Convert Pydantic model to dict
        user_dict = user.dict()
        print("Received user data:", user_dict)

        # Normalize email before storing
        user_dict['email'] = UserService.normalize_email(user_dict['email'])

        # Convert domain preferences to dict format (already in correct format)
        # No need to modify domain_pref_one and domain_pref_two as they're already dicts

        # Remove explicit None setting - let ODMantic use default_factory=dict
        # The optional fields will automatically get empty dicts as defaults

        # Create ODMantic user instance
        new_user = User(**user_dict)

        # Save using ODMantic engine
        saved_user = await engine.save(new_user)

        return saved_user
        
    @staticmethod
    async def get_user(user_id: str) -> Optional[User]:
        """Get user by ID"""
        engine = get_database()
        try:
            # Convert string ID to ObjectId if needed
            obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
            user = await engine.find_one(User, User.id == obj_id)
            return user
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email ID"""
        engine = get_database()
        try:
            user = await engine.find_one(User, User.email == email)
            return user
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    async def get_users() -> List[User]:
        """Get all users"""
        engine = get_database()
        users = await engine.find(User)
        return list(users)
    
    @staticmethod
    async def get_users_for_admin() -> List[dict]:
        """Get all users formatted for admin response (with string IDs)"""
        import logging
        logger = logging.getLogger("user_service")
        engine = get_database()
        users = await engine.find(User)
        
        formatted_users = []
        for user in users:
            user_dict = user.dict()
            user_dict['id'] = str(user.id)
            formatted_users.append(user_dict)
        
        logger.info(f"Fetched {len(formatted_users)} users for admin")
        return formatted_users
    
    @staticmethod
    async def get_users_by_group(group_number: int) -> List[User]:
        """Get all users by group number"""
        engine = get_database()
        users = await engine.find(User, User.groupNumber == group_number)
        return list(users)
    
    @staticmethod
    async def update_screening(user_id: str, update: screeningUpdate) -> Optional[User]:
        """Update user's screening status by user_id"""
        engine = get_database()
        user = await UserService.get_user(user_id)
        if not user:
            return None
            
        # Convert update to dict
        update_dict = update.dict()
        
        # Handle domain updates if provided
        if update.domains is not None:
            # Overwrite existing domains with new ones from payload
            user.domains = update.domains
            
            # Remove domains from update_dict since we handle it separately
            update_dict.pop('domains', None)
        
        # Update the screening field
        user.screening = update_dict
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def update_screening_by_email(email: str, update: screeningUpdate) -> Optional[User]:
        """Update user's screening status by email"""
        engine = get_database()
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
            
        # Convert update to dict
        update_dict = update.dict()
        
        # Handle domain updates if provided
        if update.domains is not None:
            # Overwrite existing domains with new ones from payload
            user.domains = update.domains
            
            # Remove domains from update_dict since we handle it separately
            update_dict.pop('domains', None)
        
        # Update the screening field
        user.screening = update_dict
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def update_gd(user_id: str, update: GDUpdate) -> Optional[User]:
        """Update user's GD status by user_id"""
        engine = get_database()
        user = await UserService.get_user(user_id)
        if not user:
            return None
            
        # Convert update to dict
        update_dict = update.dict()
        
        # Update the gd field
        user.gd = update_dict
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def update_gd_by_email(email: str, update: GDUpdate) -> Optional[User]:
        """Update user's GD status by email"""
        engine = get_database()
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
            
        # Convert update to dict
        update_dict = update.dict()
        
        # Update the gd field
        user.gd = update_dict
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def update_pi(user_id: str, update: PIUpdate) -> Optional[User]:
        """Update user's PI status by user_id"""
        engine = get_database()
        user = await UserService.get_user(user_id)
        if not user:
            return None
            
        # Convert update to dict
        update_dict = update.dict()
        
        # Update the pi field
        user.pi = update_dict
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def update_pi_by_email(email: str, update: PIUpdate) -> Optional[User]:
        """Update user's PI status by email"""
        engine = get_database()
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
            
        # Convert update to dict
        update_dict = update.dict()
        
        # Update the pi field
        user.pi = update_dict
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def update_task(user_id: str, update: TaskUpdate) -> Optional[User]:
        """Update user's task status by user_id"""
        engine = get_database()
        user = await UserService.get_user(user_id)
        if not user:
            return None
            
        # Convert update to dict
        update_dict = update.dict()
        
        # Update the task field
        user.task = update_dict
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def update_task_by_email(email: str, update: TaskUpdate) -> Optional[User]:
        """Update user's task status by email"""
        engine = get_database()
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
        
        # Convert update to dict
        update_dict = update.dict()
        
        # Get existing task data or create empty structure
        current_task = user.task if user.task else {"status": "", "tasks": []}
        
        # Update status
        current_task["status"] = update_dict["status"]
        
        # Handle tasks array - add new or update existing based on domain
        if "tasks" not in current_task:
            current_task["tasks"] = []
        
        # Process each new task
        for new_task in update_dict["tasks"]:
            domain = new_task["domain"]
            url = str(new_task["url"])  # Convert HttpUrl to string
            status = "completed" if url else "pending"

            # Check if a task with this domain already exists
            existing_task_index = None
            for i, existing_task in enumerate(current_task["tasks"]):
                if existing_task.get("domain") == domain:
                    existing_task_index = i
                    break

            # Update existing task or add new one
            if existing_task_index is not None:
                # Update existing task
                current_task["tasks"][existing_task_index]["url"] = url
                current_task["tasks"][existing_task_index]["status"] = status
            else:
                # Add new task
                current_task["tasks"].append({
                    "domain": domain,
                    "url": url,
                    "status": status
                })
        
        # Update the task field
        user.task = current_task
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def get_last_group_number() -> int:
        """Get the highest group number from all users"""
        engine = get_database()
        users = await engine.find(User)
        max_group = 0
        for user in users:
            if user.groupNumber and user.groupNumber > max_group:
                max_group = user.groupNumber
        return max_group
    
    @staticmethod
    async def change_user_groups(emails: List[str], target_group_number: int):
        """
        Change group number for multiple users to an existing group and update their times
        """
        engine = get_database()
        
        # First, check if the target group exists
        target_group_users = await engine.find(User, User.groupNumber == target_group_number)
        target_group_list = list(target_group_users)
        
        if not target_group_list:
            raise ValueError(f"Target group {target_group_number} does not exist")
        
        # Get the schedule from the first user in the target group
        reference_user = target_group_list[0]
        if not reference_user.gd or not reference_user.screening or not reference_user.pi:
            raise ValueError(f"Target group {target_group_number} does not have complete scheduling information")
        
        # Extract scheduling information from the reference user
        target_gd_time = reference_user.gd.get("datetime")
        target_screening_time = reference_user.screening.get("datetime")
        target_pi_time = reference_user.pi.get("datetime")
        
        if not all([target_gd_time, target_screening_time, target_pi_time]):
            raise ValueError(f"Target group {target_group_number} has incomplete scheduling times")
        
        # Find batch number from remarks (if available)
        target_batch_info = reference_user.gd.get("remarks", "")
        
        # Process the users to be moved
        updated_users = []
        failed = []
        
        for email in emails:
            try:
                user = await UserService.get_user_by_email(email)
                if not user:
                    failed.append({"email": email, "reason": "User not found"})
                    continue
                
                # Update user's group number
                user.groupNumber = target_group_number
                
                # Update scheduling times to match the target group
                user.gd = {
                    "status": user.gd.get("status", "scheduled") if user.gd else "scheduled",
                    "datetime": target_gd_time,
                    "remarks": target_batch_info
                }
                
                user.screening = {
                    "status": user.screening.get("status", "scheduled") if user.screening else "scheduled",
                    "datetime": target_screening_time,
                    "remarks": target_batch_info
                }
                
                user.pi = {
                    "status": user.pi.get("status", "scheduled") if user.pi else "scheduled",
                    "datetime": target_pi_time,
                    "remarks": [target_batch_info] if isinstance(user.pi.get("remarks"), list) else [target_batch_info]
                }
                
                # Save the updated user
                await engine.save(user)
                updated_users.append(email)
                
            except Exception as e:
                failed.append({"email": email, "reason": str(e)})
        
        return {
            "updated": updated_users,
            "failed": failed,
            "targetGroupNumber": target_group_number,
            "schedulingTimes": {
                "gdTime": target_gd_time,
                "screeningTime": target_screening_time,
                "piTime": target_pi_time
            }
        }
    
    @staticmethod
    async def bulk_create_rounds(emails: List[str], batch_size: int, start_date: str, start_time: str, end_time: str, round_duration: int):
        """
        Bulk create rounds for multiple users with scheduling logic
        """
        from datetime import datetime, timedelta
        import random
        import math
        
        engine = get_database()
        
        # Fetch users by emails
        users = []
        failed = []
        
        for email in emails:
            user = await UserService.get_user_by_email(email)
            if user:
                users.append(user)
            else:
                failed.append({"email": email, "reason": "User not found"})
        
        if not users:
            return {"totalUsersScheduled": 0, "totalBatches": 0, "batches": [], "failed": failed}
        
        # Randomly shuffle users for distribution
        random.shuffle(users)
        
        # Get next group number
        last_group = await UserService.get_last_group_number()
        current_group = last_group + 1
        
        # Parse start date and times
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))
        
        # Calculate available minutes per day
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        total_minutes_per_day = end_minutes - start_minutes
        
        # With overlapping batches, each new batch starts when previous moves to screening
        # So interval between batches is just round_duration (not 3 * round_duration)
        # But we need enough time for the last batch to complete all 3 rounds
        # So total time needed = (num_batches - 1) * round_duration + 3 * round_duration
        
        # Create user batches
        user_batches = []
        for i in range(0, len(users), batch_size):
            user_batches.append(users[i:i + batch_size])
        
        # Calculate how many batches can fit in one day with overlapping schedule
        # Time for n batches = (n-1) * round_duration + 3 * round_duration
        # Solving: total_minutes >= (n-1) * round_duration + 3 * round_duration
        # total_minutes >= n * round_duration + 2 * round_duration
        # n <= (total_minutes - 2 * round_duration) / round_duration
        max_batches_per_day = max(1, (total_minutes_per_day - 2 * round_duration) // round_duration + 1)
        
        if total_minutes_per_day < 3 * round_duration:
            raise ValueError("Not enough time in the day to complete even one batch (need at least 3 * roundDuration minutes)")
        
        # Schedule batches
        batches = []
        batch_number = 1
        current_date = start_date_obj
        batches_scheduled_today = 0
        
        for user_batch in user_batches:
            # Check if we need to move to next day
            if batches_scheduled_today >= max_batches_per_day:
                # Move to next day and skip Sundays
                current_date += timedelta(days=1)
                while current_date.weekday() == 6:  # Skip Sundays (6 = Sunday)
                    current_date += timedelta(days=1)
                batches_scheduled_today = 0
            
            # Calculate start time for this batch (overlapping schedule)
            # Each batch starts round_duration minutes after the previous batch
            batch_offset_minutes = batches_scheduled_today * round_duration
            batch_start_minutes = start_minutes + batch_offset_minutes
            batch_start_hour = batch_start_minutes // 60
            batch_start_min = batch_start_minutes % 60
            
            # Check if this batch would finish beyond end time
            batch_end_minutes = batch_start_minutes + (3 * round_duration)
            if batch_end_minutes > end_minutes:
                # Move to next day
                current_date += timedelta(days=1)
                while current_date.weekday() == 6:  # Skip Sundays
                    current_date += timedelta(days=1)
                batches_scheduled_today = 0
                batch_start_minutes = start_minutes
                batch_start_hour = start_hour
                batch_start_min = start_min
            
            # Create datetime objects for the three rounds
            gd_time = datetime.combine(current_date, datetime.min.time().replace(
                hour=batch_start_hour, minute=batch_start_min))
            screening_time = gd_time + timedelta(minutes=round_duration)
            interview_time = screening_time + timedelta(minutes=round_duration)
            
            # Update users with group number and scheduled status
            batch_emails = []
            for user in user_batch:
                user.groupNumber = current_group
                
                # Set status to scheduled for all rounds
                user.gd = {
                    "status": "scheduled",
                    "datetime": gd_time.isoformat(),
                    "remarks": f"Batch {batch_number} - Group {current_group}"
                }
                user.screening = {
                    "status": "scheduled", 
                    "datetime": screening_time.isoformat(),
                    "remarks": f"Batch {batch_number} - Group {current_group}"
                }
                user.pi = {
                    "status": "scheduled",
                    "datetime": interview_time.isoformat(), 
                    "remarks": [f"Batch {batch_number} - Group {current_group}"]
                }
                
                await engine.save(user)
                batch_emails.append(user.email)
            
            # Create batch info
            batch_info = {
                "batchNumber": batch_number,
                "groupNumber": current_group,
                "users": batch_emails,
                "gdTime": gd_time.strftime("%H:%M"),
                "screeningTime": screening_time.strftime("%H:%M"),
                "interviewTime": interview_time.strftime("%H:%M"),
                "date": current_date.strftime("%Y-%m-%d")
            }
            batches.append(batch_info)
            
            # Increment counters
            batch_number += 1
            current_group += 1
            batches_scheduled_today += 1
        
        return {
            "totalUsersScheduled": len(users),
            "totalBatches": len(user_batches),
            "batches": batches,
            "failed": failed
        }
    
    @staticmethod
    async def toggle_shortlist_users(emails: List[str]) -> dict:
        """Toggle shortlist status for multiple users and manage tasks"""
        engine = get_database()
        updated_users = []
        failed_users = []
        
        for email in emails:
            try:
                user = await UserService.get_user_by_email(email)
                if not user:
                    failed_users.append({"email": email, "reason": "User not found"})
                    continue
                
                # Get current shortlisted status, default to False if field doesn't exist
                current_shortlisted = getattr(user, 'shortlisted', False)
                
                # Toggle shortlisted status
                user.shortlisted = not current_shortlisted
                
                if user.shortlisted:
                    # User is being shortlisted - create tasks for all domains
                    tasks = []
                    for domain in user.domains:
                        tasks.append({
                            "status": "pending",
                            "domain": domain,
                            "url": ""
                        })
                    
                    user.task = {
                        "status": "pending",
                        "tasks": tasks
                    }
                else:
                    # User is being un-shortlisted - remove tasks
                    user.task = {}
                
                # Save updated user
                updated_user = await engine.save(user)
                updated_users.append(updated_user.email)
                
            except Exception as e:
                failed_users.append({"email": email, "reason": str(e)})
        
        return {
            "updated": updated_users,
            "failed": failed_users
        }
    
    @staticmethod
    async def update_task_status_by_email(email: str, task_update: TaskStatusUpdate) -> Optional[User]:
        """Update specific task status to completed and add URL"""
        engine = get_database()
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
        
        # Get shortlisted status, default to False if field doesn't exist
        is_shortlisted = getattr(user, 'shortlisted', False)
        
        if not is_shortlisted:
            raise ValueError("User is not shortlisted")
        
        # Get current task data
        current_task = user.task if user.task else {"status": "pending", "tasks": []}
        
        # Find and update the specific task
        task_found = False
        for task in current_task.get("tasks", []):
            if task.get("domain") == task_update.domain:
                task["status"] = "completed"
                task["url"] = str(task_update.url)
                task_found = True
                break
        
        if not task_found:
            raise ValueError(f"Task with domain '{task_update.domain}' not found")
        
        # Check if all tasks are completed
        all_completed = all(
            task.get("status") == "completed" 
            for task in current_task.get("tasks", [])
        )
        
        if all_completed:
            current_task["status"] = "completed"
        else:
            current_task["status"] = "in_progress"
        
        # Update the task field
        user.task = current_task
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def migrate_add_shortlisted_field() -> dict:
        """Migration function to add shortlisted field to all existing users"""
        engine = get_database()
        updated_count = 0
        failed_count = 0
        
        try:
            # Use MongoDB operations directly for the migration
            from pymongo import UpdateOne
            
            # Get the MongoDB collection directly
            collection = engine.get_collection(User)
            
            # Find all documents that don't have the shortlisted field
            documents_without_field = await collection.count_documents({"shortlisted": {"$exists": False}})
            
            if documents_without_field == 0:
                return {
                    "message": "Migration completed - no users needed updating",
                    "updated_users": 0,
                    "failed_users": 0
                }
            
            # Update all documents that don't have the shortlisted field
            result = await collection.update_many(
                {"shortlisted": {"$exists": False}},
                {"$set": {"shortlisted": False}}
            )
            
            updated_count = result.modified_count
            
            return {
                "message": "Migration completed",
                "updated_users": updated_count,
                "failed_users": 0,
                "documents_found_without_field": documents_without_field
            }
            
        except Exception as e:
            return {
                "message": "Migration failed",
                "error": str(e),
                "updated_users": updated_count,
                "failed_users": failed_count
            }
    
    @staticmethod
    async def update_attendance_by_email(email: str, is_present: bool) -> Optional[User]:
        """Update user's attendance status by email"""
        engine = get_database()
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
            
        # Update the attendance field
        user.isPresent = is_present
        
        # Save the updated user
        updated_user = await engine.save(user)
        return updated_user
    
    @staticmethod
    async def bulk_assign_slots(emails: List[str], assigned_slot: str) -> dict:
        """Assign slots to multiple users in bulk"""
        engine = get_database()
        updated_count = 0
        failed_count = 0
        failed_emails = []

        # Remove duplicate emails
        unique_emails = list(set(emails))

        for email in unique_emails:
            try:
                user = await UserService.get_user_by_email(email)
                if user:
                    user.assignedSlot = assigned_slot
                    await engine.save(user)
                    updated_count += 1
                else:
                    failed_count += 1
                    failed_emails.append(email)
            except Exception as e:
                print(f"Error updating slot for {email}: {e}")
                failed_count += 1
                failed_emails.append(email)

        return {
            "message": f"Bulk slot assignment completed. Updated: {updated_count}, Failed: {failed_count}",
            "updated_count": updated_count,
            "failed_count": failed_count,
            "failed_emails": failed_emails
        }