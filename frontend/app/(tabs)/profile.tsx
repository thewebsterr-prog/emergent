import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

export default function ProfileScreen() {
  const profileSections = [
    {
      title: 'Account',
      items: [
        { icon: 'person-outline', label: 'Guest User', subtitle: 'guest@example.com' },
      ],
    },
    {
      title: 'Preferences',
      items: [
        { icon: 'notifications-outline', label: 'Notifications', onPress: () => {} },
        { icon: 'language-outline', label: 'Language', subtitle: 'English', onPress: () => {} },
        { icon: 'moon-outline', label: 'Dark Mode', onPress: () => {} },
      ],
    },
    {
      title: 'Support',
      items: [
        { icon: 'help-circle-outline', label: 'Help Center', onPress: () => {} },
        { icon: 'chatbubble-outline', label: 'Contact Us', onPress: () => {} },
        { icon: 'shield-outline', label: 'Privacy Policy', onPress: () => {} },
        { icon: 'document-text-outline', label: 'Terms of Service', onPress: () => {} },
      ],
    },
  ];

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <Ionicons name="person" size={48} color="#FFF" />
          </View>
          <Text style={styles.name}>Guest User</Text>
          <Text style={styles.email}>guest@example.com</Text>
        </View>

        {profileSections.map((section, sectionIndex) => (
          <View key={sectionIndex} style={styles.section}>
            <Text style={styles.sectionTitle}>{section.title}</Text>
            <View style={styles.sectionContent}>
              {section.items.map((item, itemIndex) => (
                <TouchableOpacity
                  key={itemIndex}
                  style={[
                    styles.item,
                    itemIndex === section.items.length - 1 && styles.itemLast,
                  ]}
                  onPress={item.onPress}
                  disabled={!item.onPress}
                >
                  <View style={styles.itemLeft}>
                    <Ionicons name={item.icon as any} size={24} color="#666" />
                    <View style={styles.itemText}>
                      <Text style={styles.itemLabel}>{item.label}</Text>
                      {item.subtitle && (
                        <Text style={styles.itemSubtitle}>{item.subtitle}</Text>
                      )}
                    </View>
                  </View>
                  {item.onPress && (
                    <Ionicons name="chevron-forward" size={20} color="#999" />
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ))}

        <View style={styles.versionContainer}>
          <Text style={styles.versionText}>Version 1.0.0</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    backgroundColor: '#FFF',
    alignItems: 'center',
    paddingVertical: 32,
    marginBottom: 16,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#FF6B35',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
    marginBottom: 4,
  },
  email: {
    fontSize: 14,
    color: '#999',
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#999',
    marginLeft: 16,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  sectionContent: {
    backgroundColor: '#FFF',
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  itemLast: {
    borderBottomWidth: 0,
  },
  itemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  itemText: {
    marginLeft: 16,
    flex: 1,
  },
  itemLabel: {
    fontSize: 16,
    color: '#333',
    marginBottom: 2,
  },
  itemSubtitle: {
    fontSize: 14,
    color: '#999',
  },
  versionContainer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  versionText: {
    fontSize: 12,
    color: '#999',
  },
});