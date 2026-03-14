export const buildStartDate = () => new Date().toISOString().split('T')[0];

export const mapPlanToCalendarEvents = (plan) => {
  if (!plan || !Array.isArray(plan.weeks)) {
    return [];
  }

  const events = [];
  plan.weeks.forEach((week, weekIndex) => {
    if (!week || !Array.isArray(week.days)) {
      return;
    }

    week.days.forEach((day, dayIndex) => {
      if (!day || !day.date) {
        return;
      }

      const workoutType = day.workoutType || 'Workout';
      const exercises = Array.isArray(day.exercises) ? day.exercises : [];
      const isRest = workoutType.toLowerCase().includes('rest') || exercises.length === 0;

      events.push({
        id: `${weekIndex + 1}-${dayIndex + 1}-${day.date}`,
        title: workoutType,
        date: day.date,
        type: isRest ? 'rest' : 'workout',
        metadata: { exercises },
      });
    });
  });

  return events;
};
