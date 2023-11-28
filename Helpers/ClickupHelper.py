import os

import pyclickup

clickup_token = os.getenv("CLICKUP_TOKEN")
clickup = pyclickup.ClickUp(clickup_token)
main_team = clickup.teams[0]
main_space = main_team.spaces[1]
main_project = main_space.projects[0]
bug_list_index = len(main_project.lists) - 1
bug_list = main_project.lists[bug_list_index]
statuses_list = main_project.statuses
all_tasks = bug_list.get_all_tasks()


def updateAllTasks():
    global all_tasks
    all_tasks = bug_list.get_all_tasks()


def getTask(task_id):
    for task in all_tasks:
        if task.id == task_id:
            return task
    return None


def createTask(name, description):
    task = bug_list.create_task(name, description)
    updateAllTasks()
    return getTask(task)


def getAllTasks():
    return all_tasks
