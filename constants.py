class IterationFields:
    Name = 'name'
    Id = 'id'
    StartDate = 'startDate'
    FinishDate = 'finishDate'


class WorkItemTypes:
    Epic = 'Epic'
    Feature = 'Feature'
    PBI = 'Product Backlog Item'
    Bug = 'Bug'
    Task = 'Task'

    All_Types = [Epic, Feature, PBI, Bug, Task]


class WorkItemStates:
    New = 'New'
    InProgress = 'In Progress'
    ToDo = 'To Do'
    Done = 'Done'
    Committed = 'Committed'

    All_States = [New, InProgress, ToDo, Done, Committed]


class WorkItemFields:
    BacklogPriority = 'Microsoft.VSTS.Common.BacklogPriority'
    Effort = 'Microsoft.VSTS.Scheduling.Effort'
    Id = 'System.Id'
    Iteration = 'System.IterationPath'
    Parent = 'System.Parent'
    RemainingWork = 'Microsoft.VSTS.Scheduling.RemainingWork'
    State = 'System.State'
    Tags = 'System.Tags'
    TeamProject = 'System.TeamProject'
    Title = 'System.Title'
    WorkItemType = 'System.WorkItemType'

    All_Fields = [BacklogPriority, Effort, Id, Iteration, Parent, RemainingWork, State, Tags, TeamProject, Title,
                  WorkItemType]


class PythonCustomFields:
    CalculatedCapacity = 'PythonCustom.CalculatedCapacity'
    RemainingWork = 'PythonCustom.RemainingWork'

    All_Fields = [CalculatedCapacity, RemainingWork]


class BoardsScrumWorkItemCustomFields:
    InternalTargetDate = 'Custom.InternalTargetDate'
    ExternalTargetDate = 'Custom.ExternalTargetDate'

    All_Fields = [InternalTargetDate, ExternalTargetDate]
