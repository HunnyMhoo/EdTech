export interface Question {
  id: string;
  text: string;
  // Add other question-related fields if necessary
}

export interface Mission {
  id: string;
  date: string; // Or Date object, depending on API
  questions: Question[];
  status: 'not_started' | 'in_progress' | 'complete';
  // Add other mission-related fields if necessary
}

export const fetchDailyMission = async (): Promise<Mission> => {
  const MOCK_API_ENDPOINT = '/api/missions/today'; // Replace with actual endpoint

  try {
    // Simulate API call for now
    // const response = await fetch(MOCK_API_ENDPOINT);

    // if (!response.ok) {
    //   // Log more detailed error information in a real app
    //   console.error('API error:', response.status, await response.text());
    //   throw new Error(`Failed to fetch mission: ${response.status}`);
    // }
    // const data: Mission = await response.json();
    // return data;

    // --- Mocked Data for Development ---
    // Remove this block when backend is ready
    console.log('Using mocked mission data');
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    const mockMission: Mission = {
      id: 'mission_123',
      date: new Date().toISOString().split('T')[0],
      questions: [
        { id: 'q1', text: 'What is the capital of France?' },
        { id: 'q2', text: 'Solve: 2 + 2 = ?' },
        { id: 'q3', text: 'What is H2O?' },
        { id: 'q4', text: 'Who wrote Hamlet?' },
        { id: 'q5', text: 'What is the largest planet in our solar system?' },
      ],
      status: 'not_started',
    };
    // Simulate a chance of error for testing
    // if (Math.random() < 0.2) {
    //   console.error('Simulated API error: Failed to fetch mission');
    //   throw new Error('Simulated API error: Failed to fetch mission');
    // }
    return mockMission;
    // --- End of Mocked Data ---

  } catch (error) {
    // Log error to a monitoring service in a real app
    console.error('Error fetching daily mission:', error);
    // Re-throw a more user-friendly error or handle specific error types
    if (error instanceof Error) {
      throw new Error(`Could not retrieve daily mission: ${error.message}`);
    }
    throw new Error('An unknown error occurred while fetching the daily mission.');
  }
}; 