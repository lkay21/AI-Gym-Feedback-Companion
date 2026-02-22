import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ActivityIndicator,
  TouchableOpacity,
  Modal,
  FlatList,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Calendar } from 'react-native-calendars';
import { chatAPI } from '../services/api';
import { buildStartDate, mapPlanToCalendarEvents } from '../utils/planMapping';

export default function PlanScreen() {
  const [plan, setPlan] = useState(null);
  const [events, setEvents] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalVisible, setModalVisible] = useState(false);

  const fetchPlan = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      // Call the plan generation endpoint (uses authenticated user's health profile)
      const result = await chatAPI.generatePlan();

      if (!result.success) {
        // Check if user needs to complete health onboarding
        if (result.data?.requiresOnboarding) {
          throw new Error('Please complete your health profile first in the chat.');
        }
        throw new Error(result.error || 'Failed to fetch plan');
      }

      const structuredPlan = result.data?.structuredPlan;
      if (!structuredPlan) {
        throw new Error('No structured plan returned');
      }

      setPlan(structuredPlan);
      setEvents(mapPlanToCalendarEvents(structuredPlan));
    } catch (err) {
      setError(err.message || 'Failed to load plan');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlan();
  }, [fetchPlan]);

  const eventsByDate = useMemo(() => {
    const map = {};
    events.forEach((event) => {
      if (!map[event.date]) {
        map[event.date] = [];
      }
      map[event.date].push(event);
    });
    return map;
  }, [events]);

  const markedDates = useMemo(() => {
    const marks = {};
    events.forEach((event) => {
      marks[event.date] = {
        customStyles: {
          container: {
            backgroundColor: event.type === 'rest' ? '#1f2937' : '#7c3aed',
            borderRadius: 12,
          },
          text: {
            color: '#ffffff',
            fontWeight: '700',
          },
        },
      };
    });

    if (selectedDate) {
      marks[selectedDate] = {
        ...(marks[selectedDate] || {}),
        customStyles: {
          container: {
            ...(marks[selectedDate]?.customStyles?.container || {}),
            borderWidth: 2,
            borderColor: '#facc15',
          },
          text: {
            ...(marks[selectedDate]?.customStyles?.text || {}),
            color: '#ffffff',
          },
        },
      };
    }

    return marks;
  }, [events, selectedDate]);

  const handleDayPress = (day) => {
    const date = day.dateString;
    setSelectedDate(date);
    const dayEvents = eventsByDate[date] || [];
    setSelectedEvent(dayEvents[0] || null);
    setModalVisible(true);
  };

  const renderExercise = ({ item }) => (
    <View style={styles.exerciseRow}>
      <Text style={styles.exerciseName}>{item.name}</Text>
      <Text style={styles.exerciseMeta}>
        {item.sets} sets • {item.reps} reps {item.weight ? `• ${item.weight}` : ''}
      </Text>
    </View>
  );

  return (
    <LinearGradient colors={['#0f172a', '#1e1b4b']} style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <Text style={styles.title}>Your Fitness Plan</Text>
          <Text style={styles.subtitle}>{plan?.planName || 'Plan Overview'}</Text>
        </View>

        {loading ? (
          <View style={styles.centered}>
            <ActivityIndicator size="large" color="#facc15" />
            <Text style={styles.loadingText}>Loading plan...</Text>
          </View>
        ) : error ? (
          <View style={styles.centered}>
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity style={styles.retryButton} onPress={fetchPlan}>
              <Text style={styles.retryButtonText}>Try Again</Text>
            </TouchableOpacity>
          </View>
        ) : events.length === 0 ? (
          <View style={styles.centered}>
            <Text style={styles.emptyText}>No plan available yet.</Text>
          </View>
        ) : (
          <View style={styles.calendarWrapper}>
            <Calendar
              markingType="custom"
              markedDates={markedDates}
              onDayPress={handleDayPress}
              theme={{
                calendarBackground: '#111827',
                dayTextColor: '#e5e7eb',
                monthTextColor: '#facc15',
                textMonthFontWeight: '700',
                textDayFontWeight: '600',
                textDayHeaderFontWeight: '700',
              }}
            />
            <Text style={styles.calendarHint}>Tap a day to view workout details</Text>
          </View>
        )}

        <Modal
          visible={modalVisible}
          animationType="slide"
          transparent
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalCard}>
              <Text style={styles.modalTitle}>{selectedEvent?.title || 'Rest Day'}</Text>
              <Text style={styles.modalDate}>{selectedDate}</Text>

              {selectedEvent?.metadata?.exercises?.length ? (
                <FlatList
                  data={selectedEvent.metadata.exercises}
                  keyExtractor={(item, index) => `${item.name}-${index}`}
                  renderItem={renderExercise}
                  contentContainerStyle={styles.exerciseList}
                />
              ) : (
                <Text style={styles.restText}>Take a rest and recover today.</Text>
              )}

              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 24,
    paddingTop: 12,
    paddingBottom: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#facc15',
  },
  subtitle: {
    fontSize: 14,
    color: '#cbd5f5',
    marginTop: 4,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  loadingText: {
    marginTop: 12,
    color: '#e2e8f0',
  },
  errorText: {
    color: '#fecaca',
    textAlign: 'center',
    marginBottom: 12,
  },
  retryButton: {
    backgroundColor: '#facc15',
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 20,
  },
  retryButtonText: {
    color: '#111827',
    fontWeight: '700',
  },
  emptyText: {
    color: '#e2e8f0',
    textAlign: 'center',
  },
  calendarWrapper: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  calendarHint: {
    textAlign: 'center',
    marginTop: 12,
    color: '#94a3b8',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    justifyContent: 'flex-end',
  },
  modalCard: {
    backgroundColor: '#111827',
    padding: 24,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    minHeight: 300,
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#facc15',
  },
  modalDate: {
    color: '#94a3b8',
    marginTop: 6,
  },
  exerciseList: {
    marginTop: 16,
  },
  exerciseRow: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1f2937',
  },
  exerciseName: {
    color: '#e5e7eb',
    fontWeight: '600',
  },
  exerciseMeta: {
    color: '#94a3b8',
    marginTop: 4,
  },
  restText: {
    marginTop: 16,
    color: '#cbd5f5',
  },
  closeButton: {
    marginTop: 20,
    alignSelf: 'center',
    backgroundColor: '#7c3aed',
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 18,
  },
  closeButtonText: {
    color: '#ffffff',
    fontWeight: '700',
  },
});
