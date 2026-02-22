import React, { useMemo, useState } from "react";
import { View, Text, StyleSheet, Pressable, Modal } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { usePathname, useRouter } from "expo-router";

export default function MenuDropdown() {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const items = useMemo(
    () => [
      { label: "ChatBot", href: "/chatbot" },
      { label: "Dashboard", href: "/dashboard" },
      { label: "Insights", href: "/insights" },
      { label: "Snapshot", href: "/snapshot" },
    ],
    []
  );

  const go = (href) => {
    setOpen(false);
    if (pathname === href) return;
    router.push(href);
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
              const active = pathname === it.href;
              return (
                <Pressable
                  key={it.href}
                  onPress={() => go(it.href)}
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