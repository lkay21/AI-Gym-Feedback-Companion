import React from 'react';
import { View, Text, FlatList } from 'react-native';

export default function WorkoutSnapshot({ workout }) {
  const workoutType = workout?.workoutType?.trim() || '';
  const exercises = Array.isArray(workout?.exercises) ? workout.exercises : [];
  const isRestDay =
    !workoutType || workoutType.toLowerCase().includes('rest') || exercises.length === 0;

  const headerTitle = isRestDay ? 'Recovery Day' : workoutType;

  return (
    <View className="rounded-2xl bg-slate-900 p-5">
      <Text className="text-xl font-bold text-yellow-400">{headerTitle}</Text>

      {isRestDay ? (
        <Text className="mt-3 text-sm text-slate-300">
          Recovery Day
        </Text>
      ) : (
        <FlatList
          data={exercises}
          keyExtractor={(item, index) => `${item?.name || 'exercise'}-${index}`}
          renderItem={({ item }) => (
            <View className="mt-4 rounded-xl bg-slate-800 p-4">
              <Text className="text-base font-semibold text-slate-100">
                {item?.name || 'Exercise'}
              </Text>
              <Text className="mt-1 text-sm text-slate-300">
                {item?.sets || 0} x {item?.reps || 0}
                {item?.weight ? ` x ${item.weight}` : ''}
              </Text>
            </View>
          )}
        />
      )}
    </View>
  );
}
