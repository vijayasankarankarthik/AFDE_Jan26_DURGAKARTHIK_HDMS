-- ============================================================
-- database/seed.sql
-- Helpdesk Ticket Management System — Sample Data
--
-- Run after init.sql to populate the database with realistic
-- sample tickets for development and demonstration.
--
-- psql -U postgres -d helpdesk_db -f database/seed.sql
-- ============================================================

-- Clear existing data (safe for development resets)
TRUNCATE TABLE tickets RESTART IDENTITY CASCADE;

-- ─── Sample Tickets ───────────────────────────────────────
INSERT INTO tickets
    (employee_name, department, issue_category, description, priority, status, resolution_notes, created_at)
VALUES
-- Open tickets
(
    'Alice Johnson',
    'Engineering',
    'VPN Issue',
    'I am unable to connect to the company VPN from my home office. I have tried restarting the VPN client and my router but the issue persists. The error message says "Authentication Failed" even though my credentials are correct.',
    'High',
    'Open',
    NULL,
    NOW() - INTERVAL '2 hours'
),
(
    'Bob Martinez',
    'Finance',
    'Password Reset',
    'My Active Directory account has been locked out after several failed login attempts. I need my password reset urgently as I have a budget approval deadline today.',
    'Critical',
    'Open',
    NULL,
    NOW() - INTERVAL '45 minutes'
),
(
    'Carol White',
    'Marketing',
    'Software Installation',
    'I need Adobe Creative Suite (Photoshop, Illustrator, InDesign) installed on my workstation for a product launch campaign starting next week. License has been approved by my manager.',
    'Medium',
    'Open',
    NULL,
    NOW() - INTERVAL '3 hours'
),
(
    'David Lee',
    'Sales',
    'Laptop Issue',
    'My laptop screen is flickering intermittently and sometimes goes completely black for a few seconds. This happens especially when I am on video calls with clients, which is very disruptive.',
    'High',
    'Open',
    NULL,
    NOW() - INTERVAL '1 day'
),
(
    'Emma Thompson',
    'Human Resources',
    'Email Access',
    'I cannot access my company email on my mobile phone after the recent IT policy update. My desktop email client works fine but the mobile app keeps asking for re-authentication.',
    'Medium',
    'Open',
    NULL,
    NOW() - INTERVAL '5 hours'
),

-- In Progress tickets
(
    'Frank Garcia',
    'Operations',
    'Network Connectivity',
    'The entire 3rd floor is experiencing extremely slow internet speeds. Downloads that normally take seconds are taking several minutes. Multiple employees have confirmed the issue.',
    'Critical',
    'In Progress',
    'Investigating network switch on 3rd floor. Possible faulty port causing packet loss. Running diagnostics.',
    NOW() - INTERVAL '6 hours'
),
(
    'Grace Kim',
    'Legal',
    'Software Installation',
    'I need the DocuSign desktop application installed to manage contract signatures efficiently. Currently using the web version which is missing features I need for bulk processing.',
    'Low',
    'In Progress',
    'License procurement in progress. Installation scheduled for end of day.',
    NOW() - INTERVAL '2 days'
),
(
    'Henry Brown',
    'Engineering',
    'VPN Issue',
    'VPN connects successfully but I cannot access the internal development server at 192.168.10.50. Other internal resources work fine. Issue started after the network maintenance window last Friday.',
    'High',
    'In Progress',
    'Checking firewall rules and VPN split-tunnel configuration. Coordinating with network team.',
    NOW() - INTERVAL '1 day'
),
(
    'Isabella Davis',
    'Accounting',
    'Laptop Issue',
    'My laptop battery drains from 100% to 0% in approximately 90 minutes, even with minimal usage. The battery health indicator shows "Service Recommended". I work away from a power outlet frequently.',
    'Medium',
    'In Progress',
    'Battery replacement ordered. Expected delivery in 2 business days.',
    NOW() - INTERVAL '3 days'
),

-- Resolved tickets
(
    'James Wilson',
    'Product Management',
    'Password Reset',
    'Account locked due to expired password. Need immediate access to present to stakeholders in 30 minutes.',
    'Critical',
    'Resolved',
    'Password reset completed via Active Directory. User confirmed access restored. Advised to update password manager.',
    NOW() - INTERVAL '1 week'
),
(
    'Karen Martinez',
    'Engineering',
    'Software Installation',
    'Requesting installation of Docker Desktop and VS Code with recommended extensions for a new project starting this sprint.',
    'Medium',
    'Resolved',
    'Docker Desktop 4.25.0 and VS Code with recommended extensions installed. User verified setup working.',
    NOW() - INTERVAL '5 days'
),
(
    'Liam Anderson',
    'Customer Support',
    'Email Access',
    'Outlook is crashing every time I try to open an email with an attachment. Started happening after the Windows update last Tuesday.',
    'High',
    'Resolved',
    'Repaired Office installation via Control Panel. Outlook profile recreated. Issue resolved after clearing cached files.',
    NOW() - INTERVAL '2 days'
),
(
    'Mia Rodriguez',
    'Finance',
    'Network Connectivity',
    'Cannot access the finance shared drive \\\\fileserver\\finance. Getting "Access Denied" error since yesterday morning.',
    'High',
    'Resolved',
    'Permissions issue identified — user was removed from the FINANCE_USERS security group during AD cleanup. Access restored.',
    NOW() - INTERVAL '3 days'
),
(
    'Noah Taylor',
    'Marketing',
    'Hardware Request',
    'Requesting an external monitor (at least 27 inch) and a wireless keyboard/mouse combo for my new workstation setup.',
    'Low',
    'Resolved',
    'Dell 27" P2722H monitor and Logitech MX Keys + MX Master 3 ordered. Delivered and set up by IT.',
    NOW() - INTERVAL '1 week'
),

-- Closed tickets
(
    'Olivia Jackson',
    'Operations',
    'VPN Issue',
    'VPN client showing outdated certificate warning. Cannot dismiss the warning and forced to use insecure connection option.',
    'Medium',
    'Closed',
    'VPN client updated to latest version 5.1.2. New certificate deployed via MDM. Issue resolved and verified by user.',
    NOW() - INTERVAL '2 weeks'
),
(
    'Peter Chen',
    'Sales',
    'Laptop Issue',
    'Laptop running extremely slow. Takes 10+ minutes to boot and applications lag severely. Laptop is 4 years old.',
    'Medium',
    'Closed',
    'SSD upgrade performed (HDD replaced with Samsung 860 EVO). Clean Windows 11 install. Boot time reduced to under 30 seconds.',
    NOW() - INTERVAL '10 days'
),
(
    'Quinn Foster',
    'Human Resources',
    'Software Installation',
    'Need HR Analytics Pro software installed for the annual workforce planning exercise. Approved by CTO.',
    'Low',
    'Closed',
    'HR Analytics Pro v3.2 installed and configured. License key activated. Training scheduled with vendor.',
    NOW() - INTERVAL '2 weeks'
),
(
    'Rachel Green',
    'Legal',
    'Email Access',
    'Need to set up email delegation so my assistant can manage my inbox while I am on leave next month.',
    'Low',
    'Closed',
    'Email delegation configured in Exchange Admin Center. Tested and confirmed working with user and assistant.',
    NOW() - INTERVAL '1 week'
);

-- ─── Verify seed data ─────────────────────────────────────
SELECT
    status,
    COUNT(*) AS ticket_count
FROM tickets
GROUP BY status
ORDER BY
    CASE status
        WHEN 'Open'        THEN 1
        WHEN 'In Progress' THEN 2
        WHEN 'Resolved'    THEN 3
        WHEN 'Closed'      THEN 4
    END;
