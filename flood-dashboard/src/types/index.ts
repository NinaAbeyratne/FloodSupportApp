export interface SOSRecord {
  id: number;
  referenceNumber: string;
  fullName: string;
  phoneNumber: string;
  alternatePhone: string;
  latitude: string | null;
  longitude: string | null;
  address: string;
  landmark: string;
  district: string;
  emergencyType: string;
  numberOfPeople: number;
  hasChildren: boolean;
  hasElderly: boolean;
  hasDisabled: boolean;
  hasMedicalEmergency: boolean;
  medicalDetails: string;
  waterLevel: string;
  buildingType: string;
  floorLevel: number;
  safeForHours: number;
  description: string;
  internalNotes: string | null;
  verifiedBy: string | null;
  source: string;
  hasFood: boolean;
  hasWater: boolean;
  hasPowerBank: boolean;
  batteryPercentage: number;
  status: string;
  priority: string;
  rescueTeam: string | null;
  acknowledgedAt: string | null;
  rescuedAt: string | null;
  completedAt: string | null;
  actionTaken: string | null;
  actionTakenAt: string | null;
  actionTakenBy: string | null;
  verifiedLocation: string | null;
  title: string;
  createdAt: string;
  updatedAt: string;
}

export interface APIResponse {
  success: boolean;
  data: SOSRecord[];
  pagination: {
    currentPage: number;
    totalPages: number;
    totalCount: number;
    limit: number;
    hasNextPage: boolean;
    hasPrevPage: boolean;
  };
  stats: {
    totalPeople: number;
    missingPeopleCount: number;
    byStatus: Record<string, number>;
    byPriority: Record<string, number>;
  };
}

export interface DistrictSummary {
  district: string;
  total: number;
  totalPeople: number;
  pending: number;
  verified: number;
  acknowledged: number;
  inProgress: number;
  rescued: number;
  completed: number;
  cannotContact: number;
  missing: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  trapped: number;
  foodWater: number;
  medical: number;
  rescueAssistance: number;
  missingPerson: number;
  other: number;
  hasChildren: number;
  hasElderly: number;
  hasDisabled: number;
  hasMedicalEmergency: number;
}
