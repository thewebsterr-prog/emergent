import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface OrderCardProps {
  order: {
    id: string;
    createdAt: string;
    total: number;
    status: string;
    items: any[];
  };
  onPress: () => void;
}

export default function OrderCard({ order, onPress }: OrderCardProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return '#4CAF50';
      case 'pending':
        return '#FFA500';
      case 'shipped':
        return '#2196F3';
      case 'delivered':
        return '#4CAF50';
      default:
        return '#999';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.header}>
        <View>
          <Text style={styles.orderId}>Order #{order.id.substring(0, 8)}</Text>
          <Text style={styles.date}>{formatDate(order.createdAt)}</Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(order.status) }]}>
          <Text style={styles.statusText}>{order.status}</Text>
        </View>
      </View>
      <View style={styles.divider} />
      <View style={styles.footer}>
        <View style={styles.itemsContainer}>
          <Ionicons name="cube-outline" size={16} color="#666" />
          <Text style={styles.itemsText}>{order.items.length} items</Text>
        </View>
        <Text style={styles.total}>${order.total.toFixed(2)}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  orderId: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  date: {
    fontSize: 12,
    color: '#999',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFF',
    textTransform: 'capitalize',
  },
  divider: {
    height: 1,
    backgroundColor: '#F0F0F0',
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  itemsText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 6,
  },
  total: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FF6B35',
  },
});