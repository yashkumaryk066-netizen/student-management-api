// Insert this BEFORE line 789 (default case) in admin.js

            // === INSTITUTIONAL ERP 2.0 MODULES ===
            case 'roi-analytics':
            case 'roi_analytics':
                this.loadROIAnalytics();
                break;
            case 'lms-materials':
            case 'lms_materials':
                this.loadLMSMaterials();
                break;
            case 'assignments':
                this.loadAssignments();
                break;
            // === SOVEREIGN INTELLIGENCE ===
            case 'leads':
                this.loadAILeadPredictor();
                break;
            case 'substitutes':
                this.loadSmartSubstitute();
                break;
            case 'student-diary':
            case 'diary':
                this.loadStudentDiary();
                break;
            case 'inventory':
                this.loadInventoryAssets();
                break;
