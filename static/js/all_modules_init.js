/**
 * ═══════════════════════════════════════════════════════════════
 * ALL MODULES INITIALIZATION - Using Generic Factory
 * Complete implementation of all 15+ modules
 * ═══════════════════════════════════════════════════════════════
 */

// Wait for factory to load
document.addEventListener('DOMContentLoaded', () => {
    if (!window.GenericModuleFactory) {
        console.error('Generic Module Factory not loaded!');
        return;
    }

    // ═══════════════════════════════════════════════════════════════
    // MODULE 3: FINANCE & PAYMENTS
    // ═══════════════════════════════════════════════════════════════
    window.financeModule = GenericModuleFactory.create({
        id: 'finance',
        name: 'Finance & Payments',
        icon: '💰',
        description: 'Manage fee collection, payments, and financial records',
        gradient: 'linear-gradient(135deg, #00ff88, #00d4ff)',
        apiEndpoint: '/api/payments/',
        stats: [
            {
                icon: '💵',
                label: 'Total Revenue',
                value: (data) => `₹${data.reduce((sum, p) => sum + (p.amount || 0), 0).toLocaleString()}`,
                color: '#00ff88',
                gradient: 'linear-gradient(135deg, #00ff88, #00d4ff)'
            },
            {
                icon: '⏳',
                label: 'Pending',
                value: (data) => data.filter(p => p.status === 'PENDING').length,
                color: '#f59e0b',
                gradient: 'linear-gradient(135deg, #f59e0b, #d97706)'
            },
            {
                icon: '✅',
                label: 'Collected',
                value: (data) => data.filter(p => p.status === 'PAID').length,
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            }
        ],
        columns: [
            { label: 'Student', field: 'student_name', sortable: true },
            { label: 'Amount', field: 'amount', format: 'currency' },
            { label: 'Status', field: 'status', format: 'badge' },
            { label: 'Date', field: 'created_at', format: 'date' }
        ],
        actions: [
            {
                label: 'Collect Payment',
                icon: '💳',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ],
        tableActions: [
            { label: 'View', icon: '👁️', onClick: 'showToast("View payment details", "info")' },
            { label: 'Receipt', icon: '🧾', onClick: 'showToast("Generate receipt", "info")' }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 4: EXAM & GRADING
    // ═══════════════════════════════════════════════════════════════
    window.examModule = GenericModuleFactory.create({
        id: 'exams',
        name: 'Exam & Grading',
        icon: '📝',
        description: 'Create exams, enter marks, and generate report cards',
        gradient: 'linear-gradient(135deg, #f093fb, #f5576c)',
        apiEndpoint: '/api/exams/',
        stats: [
            {
                icon: '📝',
                label: 'Total Exams',
                value: (data) => data.length,
                color: '#f093fb',
                gradient: 'linear-gradient(135deg, #f093fb, #f5576c)'
            },
            {
                icon: '📊',
                label: 'Avg Score',
                value: '85%',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            },
            {
                icon: '✅',
                label: 'Pass Rate',
                value: '92%',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            }
        ],
        columns: [
            { label: 'Exam Name', field: 'name', sortable: true },
            { label: 'Subject', field: 'subject', sortable: true },
            { label: 'Date', field: 'date', format: 'date' },
            { label: 'Max Marks', field: 'max_marks' }
        ],
        actions: [
            {
                label: 'Create Exam',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 5: COURSES & BATCHES
    // ═══════════════════════════════════════════════════════════════
    window.courseModule = GenericModuleFactory.create({
        id: 'courses',
        name: 'Courses & Batches',
        icon: '🎓',
        description: 'Manage courses, batches, and student enrollments',
        gradient: 'linear-gradient(135deg, #667eea, #764ba2)',
        apiEndpoint: '/api/courses/',
        stats: [
            {
                icon: '🎓',
                label: 'Total Courses',
                value: (data) => data.length,
                color: '#667eea',
                gradient: 'linear-gradient(135deg, #667eea, #764ba2)'
            },
            {
                icon: '👥',
                label: 'Active Batches',
                value: '12',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            },
            {
                icon: '📚',
                label: 'Enrollments',
                value: '450',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            }
        ],
        columns: [
            { label: 'Course Name', field: 'name', sortable: true },
            { label: 'Duration', field: 'duration' },
            { label: 'Batches', field: 'batch_count' },
            { label: 'Students', field: 'student_count' }
        ],
        actions: [
            {
                label: 'Add Course',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 6: LIBRARY MANAGEMENT
    // ═══════════════════════════════════════════════════════════════
    window.libraryModule = GenericModuleFactory.create({
        id: 'library',
        name: 'Library Management',
        icon: '📚',
        description: 'Manage books, issue/return, and track inventory',
        gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
        apiEndpoint: '/api/library/books/',
        stats: [
            {
                icon: '📚',
                label: 'Total Books',
                value: (data) => data.length,
                color: '#8b5cf6',
                gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
            },
            {
                icon: '📖',
                label: 'Issued',
                value: '120',
                color: '#f59e0b',
                gradient: 'linear-gradient(135deg, #f59e0b, #d97706)'
            },
            {
                icon: '⏰',
                label: 'Overdue',
                value: '8',
                color: '#ef4444',
                gradient: 'linear-gradient(135deg, #ef4444, #dc2626)'
            }
        ],
        columns: [
            { label: 'Book Title', field: 'title', sortable: true },
            { label: 'Author', field: 'author', sortable: true },
            { label: 'ISBN', field: 'isbn' },
            { label: 'Available', field: 'available_copies' }
        ],
        actions: [
            {
                label: 'Add Book',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            },
            {
                label: 'Issue Book',
                icon: '📖',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)',
                bg: 'linear-gradient(135deg, #f59e0b, #d97706)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 7: HOSTEL MANAGEMENT
    // ═══════════════════════════════════════════════════════════════
    window.hostelModule = GenericModuleFactory.create({
        id: 'hostel',
        name: 'Hostel Management',
        icon: '🏢',
        description: 'Manage rooms, allocations, and hostel operations',
        gradient: 'linear-gradient(135deg, #ec4899, #db2777)',
        apiEndpoint: '/api/hostel/rooms/',
        stats: [
            {
                icon: '🏢',
                label: 'Total Rooms',
                value: (data) => data.length,
                color: '#ec4899',
                gradient: 'linear-gradient(135deg, #ec4899, #db2777)'
            },
            {
                icon: '✅',
                label: 'Occupied',
                value: '45',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            },
            {
                icon: '🔓',
                label: 'Vacant',
                value: '15',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            }
        ],
        columns: [
            { label: 'Room No', field: 'room_number', sortable: true },
            { label: 'Type', field: 'room_type' },
            { label: 'Capacity', field: 'capacity' },
            { label: 'Occupied', field: 'occupied_count' }
        ],
        actions: [
            {
                label: 'Add Room',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 8: TRANSPORT MANAGEMENT
    // ═══════════════════════════════════════════════════════════════
    window.transportModule = GenericModuleFactory.create({
        id: 'transport',
        name: 'Transport Management',
        icon: '🚌',
        description: 'Manage vehicles, routes, and student assignments',
        gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)',
        apiEndpoint: '/api/transport/vehicles/',
        stats: [
            {
                icon: '🚌',
                label: 'Total Vehicles',
                value: (data) => data.length,
                color: '#06b6d4',
                gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)'
            },
            {
                icon: '🛣️',
                label: 'Active Routes',
                value: '8',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            },
            {
                icon: '👥',
                label: 'Students',
                value: '320',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            }
        ],
        columns: [
            { label: 'Vehicle No', field: 'vehicle_number', sortable: true },
            { label: 'Type', field: 'vehicle_type' },
            { label: 'Driver', field: 'driver_name' },
            { label: 'Route', field: 'route_name' }
        ],
        actions: [
            {
                label: 'Add Vehicle',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 9: HR & PAYROLL
    // ═══════════════════════════════════════════════════════════════
    window.hrModule = GenericModuleFactory.create({
        id: 'hr',
        name: 'HR & Payroll',
        icon: '👔',
        description: 'Manage employees, attendance, and payroll processing',
        gradient: 'linear-gradient(135deg, #f59e0b, #d97706)',
        apiEndpoint: '/api/hr/employees/',
        stats: [
            {
                icon: '👔',
                label: 'Total Employees',
                value: (data) => data.length,
                color: '#f59e0b',
                gradient: 'linear-gradient(135deg, #f59e0b, #d97706)'
            },
            {
                icon: '✅',
                label: 'Present',
                value: '45',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            },
            {
                icon: '🏖️',
                label: 'On Leave',
                value: '3',
                color: '#ef4444',
                gradient: 'linear-gradient(135deg, #ef4444, #dc2626)'
            }
        ],
        columns: [
            { label: 'Employee Name', field: 'name', sortable: true },
            { label: 'Designation', field: 'designation' },
            { label: 'Department', field: 'department' },
            { label: 'Salary', field: 'salary', format: 'currency' }
        ],
        actions: [
            {
                label: 'Add Employee',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 10: LIVE CLASSES
    // ═══════════════════════════════════════════════════════════════
    window.liveClassesModule = GenericModuleFactory.create({
        id: 'live_classes',
        name: 'Live Classes',
        icon: '🔴',
        description: 'Schedule and manage online live classes',
        gradient: 'linear-gradient(135deg, #ef4444, #dc2626)',
        apiEndpoint: '/api/live-classes/',
        stats: [
            {
                icon: '🔴',
                label: 'Live Now',
                value: '2',
                color: '#ef4444',
                gradient: 'linear-gradient(135deg, #ef4444, #dc2626)'
            },
            {
                icon: '📅',
                label: 'Upcoming',
                value: '8',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            },
            {
                icon: '✅',
                label: 'Completed',
                value: '45',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            }
        ],
        columns: [
            { label: 'Class Title', field: 'title', sortable: true },
            { label: 'Teacher', field: 'teacher_name' },
            { label: 'Date & Time', field: 'scheduled_at', format: 'date' },
            { label: 'Status', field: 'status', format: 'badge' }
        ],
        actions: [
            {
                label: 'Schedule Class',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 11: DEPARTMENT MANAGEMENT
    // ═══════════════════════════════════════════════════════════════
    window.departmentModule = GenericModuleFactory.create({
        id: 'departments',
        name: 'Department Management',
        icon: '🏛️',
        description: 'Manage departments and organizational structure',
        gradient: 'linear-gradient(135deg, #6366f1, #4f46e5)',
        apiEndpoint: '/api/departments/',
        stats: [
            {
                icon: '🏛️',
                label: 'Total Departments',
                value: (data) => data.length,
                color: '#6366f1',
                gradient: 'linear-gradient(135deg, #6366f1, #4f46e5)'
            },
            {
                icon: '👥',
                label: 'Total Staff',
                value: '48',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            }
        ],
        columns: [
            { label: 'Department Name', field: 'name', sortable: true },
            { label: 'HOD', field: 'hod_name' },
            { label: 'Staff Count', field: 'staff_count' }
        ],
        actions: [
            {
                label: 'Add Department',
                icon: '➕',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 12: NOTIFICATIONS
    // ═══════════════════════════════════════════════════════════════
    window.notificationsModule = GenericModuleFactory.create({
        id: 'notifications',
        name: 'Notifications',
        icon: '📢',
        description: 'Send and manage notifications to students and staff',
        gradient: 'linear-gradient(135deg, #a855f7, #9333ea)',
        apiEndpoint: '/api/notifications/',
        stats: [
            {
                icon: '📢',
                label: 'Total Sent',
                value: (data) => data.length,
                color: '#a855f7',
                gradient: 'linear-gradient(135deg, #a855f7, #9333ea)'
            },
            {
                icon: '✅',
                label: 'Delivered',
                value: '450',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            },
            {
                icon: '❌',
                label: 'Failed',
                value: '5',
                color: '#ef4444',
                gradient: 'linear-gradient(135deg, #ef4444, #dc2626)'
            }
        ],
        columns: [
            { label: 'Title', field: 'title', sortable: true },
            { label: 'Message', field: 'message' },
            { label: 'Sent At', field: 'created_at', format: 'date' },
            { label: 'Status', field: 'status', format: 'badge' }
        ],
        actions: [
            {
                label: 'Send Notification',
                icon: '📤',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 13: REPORTS & ANALYTICS
    // ═══════════════════════════════════════════════════════════════
    window.reportsModule = GenericModuleFactory.create({
        id: 'reports',
        name: 'Reports & Analytics',
        icon: '📈',
        description: 'View detailed reports and analytics dashboards',
        gradient: 'linear-gradient(135deg, #14b8a6, #0d9488)',
        apiEndpoint: '/api/reports/',
        stats: [
            {
                icon: '📊',
                label: 'Total Reports',
                value: '24',
                color: '#14b8a6',
                gradient: 'linear-gradient(135deg, #14b8a6, #0d9488)'
            },
            {
                icon: '📈',
                label: 'This Month',
                value: '8',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            }
        ],
        columns: [
            { label: 'Report Name', field: 'name', sortable: true },
            { label: 'Type', field: 'type' },
            { label: 'Generated', field: 'created_at', format: 'date' }
        ],
        actions: [
            {
                label: 'Generate Report',
                icon: '📊',
                onClick: 'showToast("Opening Module...", "success"); setTimeout(() => document.querySelector(".sidebar-item.active")?.click(), 500)'
            }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 14: SYSTEM LOGS
    // ═══════════════════════════════════════════════════════════════
    window.logsModule = GenericModuleFactory.create({
        id: 'logs',
        name: 'System Logs',
        icon: '📋',
        description: 'View system audit logs and activity history',
        gradient: 'linear-gradient(135deg, #64748b, #475569)',
        apiEndpoint: '/api/audit/logs/global/',
        stats: [
            {
                icon: '📋',
                label: 'Total Actions',
                value: (data) => data.length,
                color: '#64748b',
                gradient: 'linear-gradient(135deg, #64748b, #475569)'
            },
            {
                icon: '👥',
                label: 'Active Users',
                value: '12',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            },
            {
                icon: '📅',
                label: 'Today',
                value: '45',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            }
        ],
        columns: [
            { label: 'Action', field: 'action', sortable: true },
            { label: 'User', field: 'user_name' },
            { label: 'Timestamp', field: 'created_at', format: 'date' },
            { label: 'IP Address', field: 'ip_address' }
        ]
    });

    // ═══════════════════════════════════════════════════════════════
    // MODULE 15: SETTINGS
    // ═══════════════════════════════════════════════════════════════
    window.settingsModule = GenericModuleFactory.create({
        id: 'settings',
        name: 'Settings',
        icon: '⚙️',
        description: 'Configure system settings and preferences',
        gradient: 'linear-gradient(135deg, #71717a, #52525b)',
        stats: [
            {
                icon: '📦',
                label: 'Current Plan',
                value: 'Pro',
                color: '#3b82f6',
                gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)'
            },
            {
                icon: '👥',
                label: 'Users',
                value: '50/100',
                color: '#10b981',
                gradient: 'linear-gradient(135deg, #10b981, #059669)'
            },
            {
                icon: '💾',
                label: 'Storage',
                value: '2.5GB/10GB',
                color: '#f59e0b',
                gradient: 'linear-gradient(135deg, #f59e0b, #d97706)'
            }
        ],
        columns: [
            { label: 'Setting', field: 'name' },
            { label: 'Value', field: 'value' },
            { label: 'Updated', field: 'updated_at', format: 'date' }
        ],
        mockData: [
            { name: 'Institution Name', value: 'Y.S.M Education', updated_at: '2026-01-28' },
            { name: 'Email Notifications', value: 'Enabled', updated_at: '2026-01-28' },
            { name: 'SMS Notifications', value: 'Disabled', updated_at: '2026-01-28' }
        ]
    });

    console.log('✅ All Modules Initialized Successfully!');
});
