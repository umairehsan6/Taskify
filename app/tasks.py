from django.utils import timezone
from .models import task_activity_log, settings, tasks
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

def check_office_hours():
    """
    Background task to check and stop tasks that are running outside office hours or during breaks
    """
    # Get current time in Asia/Karachi timezone
    karachi_tz = pytz.timezone('Asia/Karachi')
    current_time = timezone.now().astimezone(karachi_tz)
    day_name = current_time.strftime('%A').lower()
    
    logger.info(f"Current time in Karachi: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    try:
        # Get office hours for current day
        office_hours = settings.objects.get(day=day_name)
        current_time_obj = current_time.time()
        
        logger.info(f"Office hours for {day_name}: {office_hours.start_time} - {office_hours.end_time}")
        logger.info(f"Break time: {office_hours.break_start_time} - {office_hours.break_end_time}")
        
        # Check if current time is outside office hours or during break
        should_stop = False
        reason = ""
        
        if current_time_obj < office_hours.start_time:
            should_stop = True
            reason = "Office hours have not started yet"
            logger.info(f"Current time {current_time_obj} is before office hours start {office_hours.start_time}")
        elif current_time_obj > office_hours.end_time:
            should_stop = True
            reason = "Office hours have ended"
            logger.info(f"Current time {current_time_obj} is after office hours end {office_hours.end_time}")
        elif (office_hours.break_start_time and office_hours.break_end_time and 
              office_hours.break_start_time <= current_time_obj <= office_hours.break_end_time):
            should_stop = True
            reason = "Break time has started"
            logger.info(f"Current time {current_time_obj} is during break time {office_hours.break_start_time} - {office_hours.break_end_time}")
            
        if should_stop:
            # Get all in-progress tasks
            in_progress_tasks = tasks.objects.filter(status=1)  # 1 = In Progress
            logger.info(f"Found {in_progress_tasks.count()} in-progress tasks to check")
            
            for task in in_progress_tasks:
                try:
                    # Stop the task
                    task.status = 3  # 3 = On Hold
                    task.save()
                    
                    # End the time tracking session
                    current_session = task_activity_log.objects.filter(
                        task=task,
                        end_time__isnull=True
                    ).first()
                    
                    if current_session:
                        current_session.end_time = current_time
                        current_session.calculate_duration()
                        current_session.save()
                        
                        # Log the automatic stop
                        logger.info(f"Task {task.task_name} automatically stopped: {reason}")
                    else:
                        logger.warning(f"No active session found for task {task.task_name}")
                except Exception as e:
                    logger.error(f"Error stopping task {task.task_name}: {str(e)}")
                    
    except settings.DoesNotExist:
        # If no office hours defined for this day, stop all tasks
        logger.warning(f"No office hours defined for {day_name}")
        in_progress_tasks = tasks.objects.filter(status=1)  # 1 = In Progress
        
        for task in in_progress_tasks:
            try:
                task.status = 3  # 3 = On Hold
                task.save()
                
                current_session = task_activity_log.objects.filter(
                    task=task,
                    end_time__isnull=True
                ).first()
                
                if current_session:
                    current_session.end_time = current_time
                    current_session.calculate_duration()
                    current_session.save()
                    
                    logger.info(f"Task {task.task_name} automatically stopped: No office hours defined for today")
                else:
                    logger.warning(f"No active session found for task {task.task_name}")
            except Exception as e:
                logger.error(f"Error stopping task {task.task_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in check_office_hours: {str(e)}") 