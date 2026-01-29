import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { getOrder } from '../../utils/api';
import { Order } from '../../types';

export default function OrderDetailScreen() {
  const { id } = useLocalSearchParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadOrder();
    }
  }, [id]);

  const loadOrder = async () => {
    try {
      const data = await getOrder(id as string);
      setOrder(data);
    } catch (error) {
      console.error('Error loading order:', error);
    } finally {
      setLoading(false);
    }
  };

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
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading || !order) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#FF6B35" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.statusCard}>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(order.status) }]}>
            <Ionicons name="checkmark-circle" size={32} color="#FFF" />
          </View>
          <Text style={styles.statusTitle}>Order {order.status}</Text>
          <Text style={styles.statusDate}>{formatDate(order.createdAt)}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Order Details</Text>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Order ID:</Text>
            <Text style={styles.detailValue}>#{order.id.substring(0, 12)}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Total Amount:</Text>
            <Text style={styles.detailValueHighlight}>${order.total.toFixed(2)}</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Shipping Address</Text>
          <View style={styles.addressContainer}>
            <Ionicons name="location" size={20} color="#666" />
            <View style={styles.addressText}>
              <Text style={styles.addressLine}>{order.shippingAddress.fullName}</Text>
              <Text style={styles.addressLine}>{order.shippingAddress.address}</Text>
              <Text style={styles.addressLine}>
                {order.shippingAddress.city}, {order.shippingAddress.state} {order.shippingAddress.zipCode}
              </Text>
              <Text style={styles.addressLine}>Phone: {order.shippingAddress.phone}</Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Items ({order.items.length})</Text>
          {order.items.map((item, index) => (
            <View key={index} style={styles.itemCard}>
              <Image source={{ uri: item.image }} style={styles.itemImage} />
              <View style={styles.itemDetails}>
                <Text style={styles.itemName} numberOfLines={2}>
                  {item.name}
                </Text>
                <Text style={styles.itemQuantity}>Qty: {item.quantity}</Text>
                <Text style={styles.itemPrice}>${item.price.toFixed(2)}</Text>
              </View>
              <Text style={styles.itemTotal}>${(item.price * item.quantity).toFixed(2)}</Text>
            </View>
          ))}
        </View>

        <View style={styles.section}>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Subtotal:</Text>
            <Text style={styles.summaryValue}>${order.total.toFixed(2)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Shipping:</Text>
            <Text style={styles.summaryValue}>Free</Text>
          </View>
          <View style={[styles.summaryRow, styles.totalRow]}>
            <Text style={styles.totalLabel}>Total:</Text>
            <Text style={styles.totalAmount}>${order.total.toFixed(2)}</Text>
          </View>
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
  scrollContent: {
    padding: 16,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statusCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
  },
  statusBadge: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
    textTransform: 'capitalize',
  },
  statusDate: {
    fontSize: 14,
    color: '#999',
  },
  section: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  detailValueHighlight: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FF6B35',
  },
  addressContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  addressText: {
    marginLeft: 12,
    flex: 1,
  },
  addressLine: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  itemCard: {
    flexDirection: 'row',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  itemImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: '#F5F5F5',
  },
  itemDetails: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'space-between',
  },
  itemName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  itemQuantity: {
    fontSize: 12,
    color: '#999',
  },
  itemPrice: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  itemTotal: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FF6B35',
    alignSelf: 'center',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  totalRow: {
    marginTop: 8,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },
  totalAmount: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FF6B35',
  },
});