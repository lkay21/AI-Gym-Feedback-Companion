import React, { useMemo, useState } from "react";
import { View, Text, StyleSheet, Pressable, Modal } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useNavigation, useRoute } from "@react-navigation/native";

export default function MenuDropdown() {
  const [open, setOpen] = useState(false);
  const navigation = useNavigation();
  const route = useRoute();

  const items = useMemo(
    () => [
      { label: "ChatBot", routeName: "ChatBot" },
      { label: "Dashboard", routeName: "Dashboard" },
      { label: "Insights", routeName: "Insights" },
      { label: "Snapshot", routeName: "Snapshot" },
    ],
    []
  );

  const go = (routeName) => {
    setOpen(false);
    if (route.name === routeName) return;
    navigation.navigate(routeName);
  };

  return (
    <View>
      <Pressable style={styles.menuBtn} onPress={() => setOpen(true)}>
        <Text style={styles.menuText}>Menu</Text>
        <Ionicons name="chevron-down" size={14} color="rgba(255,255,255,0.9)" />
      </Pressable>

      <Modal visible={open} transparent animationType="fade" onRequestClose={() => setOpen(false)}>
        {/* Backdrop */}
        <Pressable style={styles.backdrop} onPress={() => setOpen(false)} />

        {/* Dropdown */}
        <View style={styles.dropdownWrap}>
          <View style={styles.dropdown}>
            {items.map((it) => {
              const active = route.name === it.routeName;
              return (
                <Pressable
                  key={it.routeName}
                  onPress={() => go(it.routeName)}
                  style={[styles.item, active && styles.itemActive]}
                >
                  <Text style={[styles.itemText, active && styles.itemTextActive]}>
                    {it.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  menuBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.14)",
  },
  menuText: { color: "rgba(255,255,255,0.9)", fontSize: 12, fontWeight: "700" },

  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.25)",
  },
  dropdownWrap: {
    position: "absolute",
    top: 70,
    right: 18,
  },
  dropdown: {
    width: 160,
    borderRadius: 14,
    overflow: "hidden",
    backgroundColor: "rgba(20, 10, 40, 0.92)",
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.16)",
  },
  item: {
    paddingVertical: 12,
    paddingHorizontal: 14,
  },
  itemActive: {
    backgroundColor: "rgba(255,255,255,0.10)",
  },
  itemText: {
    color: "rgba(255,255,255,0.88)",
    fontSize: 13,
    fontWeight: "800",
  },
  itemTextActive: {
    color: "rgba(255,255,255,0.98)",
  },
});
