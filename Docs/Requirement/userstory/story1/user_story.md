User Story: Launch Daily Mission

As a logged-in student, I want to automatically receive a new 5-question daily mission each day, so that I can begin focused GAT เชื่อมโยง practice without needing to select topics manually and maintain consistent learning habits.

Acceptance Criteria

Given the student is logged in and has not started today’s mission  
When the home screen loads  
Then the student sees a prompt to begin a 5-question daily mission

Given the student begins the daily mission  
When questions are loaded  
Then exactly 5 questions from the GAT เชื่อมโยง pool are shown in sequence

Given the student has already started today’s mission  
When they reopen the app  
Then they are returned to the mission in progress without resetting

Given it is a new day  
When the student logs in  
Then a new mission with a new set of questions is generated

Given the student does not complete a mission  
When they return the next day  
Then the previous mission is replaced by a new one and progress is reset
