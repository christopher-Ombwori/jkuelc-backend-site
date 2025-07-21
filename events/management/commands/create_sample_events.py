from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from events.models import Event
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample events for testing'

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            email='admin@jkuelc.com',
            defaults={
                'name': 'Admin User',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )

        # Sample events data with detailed descriptions and important reminders
        sample_events = [
            {
                'title': 'Annual Leadership Summit 2024',
                'description': '''Join us for our flagship leadership event that brings together student leaders, industry professionals, and thought leaders for an inspiring day of learning, networking, and skill development.

This year's theme "Innovation in Leadership" explores how modern leaders can adapt to rapidly changing environments while maintaining strong team dynamics and organizational success.

What to Expect:
• Keynote speeches from renowned business leaders and entrepreneurs
• Interactive workshops on communication, conflict resolution, and strategic thinking
• Panel discussions on current leadership challenges and opportunities
• Networking sessions with professionals from various industries
• Hands-on activities to practice leadership skills in real scenarios
• Certificate of participation for all attendees

Workshop Sessions Include:
1. "Leading Through Change" - Learn how to guide teams through organizational transitions
2. "Digital Leadership" - Understanding how technology is reshaping leadership roles
3. "Emotional Intelligence in Leadership" - Developing self-awareness and empathy
4. "Strategic Decision Making" - Tools and frameworks for better choices
5. "Team Building and Collaboration" - Creating high-performing teams

This summit is designed for current and aspiring leaders who want to enhance their leadership capabilities and build meaningful connections with like-minded individuals. Whether you're leading a student organization, managing a project team, or preparing for future leadership roles, this event will provide valuable insights and practical skills.

Registration includes:
• Full access to all sessions and workshops
• Networking lunch with industry professionals
• Digital resource pack with leadership materials
• Certificate of participation
• Follow-up mentoring opportunities

Don't miss this opportunity to invest in your leadership development and connect with the next generation of leaders!''',
                'date': datetime.now().date() + timedelta(days=30),
                'time': '9:00 AM - 5:00 PM',
                'location': 'JKU Main Auditorium, Block A, Ground Floor',
                'image': 'https://images.unsplash.com/photo-1540317580384-e5d43867caa6?q=80&w=2787&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'UPCOMING',
                'is_featured': True,
                'is_registration_open': True,
                'attendees': 250,
                'important_reminders': [
                    'Please bring your student ID for registration',
                    'Dress code: Business casual attire required',
                    'Bring a notebook and pen for workshop activities',
                    'Lunch will be provided - please indicate dietary restrictions',
                    'Registration closes 24 hours before the event',
                    'Arrive 15 minutes early for check-in and seating'
                ]
            },
            {
                'title': 'Community Service Day: Environmental Conservation',
                'description': '''Give back to our community and make a positive impact on the environment through this comprehensive service day focused on environmental conservation and sustainability.

This event brings together students, faculty, community members, and environmental experts to work on various conservation projects while learning about environmental stewardship and sustainable practices.

Activities Include:
• Tree planting and urban forest restoration
• River cleanup and water quality monitoring
• Community garden development and maintenance
• Environmental education workshops for local schools
• Waste management and recycling initiatives
• Wildlife habitat restoration projects

Educational Components:
- Learn about local ecosystems and biodiversity
- Understand the impact of human activities on the environment
- Discover sustainable practices for daily life
- Network with environmental professionals and activists
- Gain hands-on experience in conservation work

Community Impact:
This event directly benefits our local community by improving air quality, enhancing biodiversity, creating green spaces, and educating future generations about environmental responsibility.

What to Bring:
• Comfortable, weather-appropriate clothing
• Closed-toe shoes suitable for outdoor work
• Water bottle and snacks
• Sun protection (hat, sunscreen)
• Work gloves (provided if needed)

Safety and Guidelines:
• All participants will receive safety briefings
• First aid stations will be available at all sites
• Professional supervision for all activities
• COVID-19 protocols will be followed

This is a family-friendly event suitable for all ages. No prior experience is required - training will be provided on-site for all activities.

Join us in making a lasting positive impact on our environment and community!''',
                'date': datetime.now().date() + timedelta(days=15),
                'time': '8:00 AM - 2:00 PM',
                'location': 'Juja Community Center and Surrounding Areas',
                'image': 'https://images.unsplash.com/photo-1593113598332-cd59a93f9724?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'UPCOMING',
                'is_featured': True,
                'is_registration_open': True,
                'attendees': 100,
                'important_reminders': [
                    'Wear comfortable outdoor clothing and closed-toe shoes',
                    'Bring water bottle and snacks',
                    'Apply sunscreen and wear a hat',
                    'Arrive at the community center by 7:45 AM for briefing',
                    'Work gloves will be provided but you can bring your own',
                    'Lunch will be provided at noon'
                ]
            },
            {
                'title': 'Digital Skills Workshop: Data Analysis & Visualization',
                'description': '''Master essential digital skills for the modern workplace in this comprehensive hands-on workshop focused on data analysis and visualization. This workshop is designed for students and professionals who want to enhance their data literacy and technical skills.

Workshop Overview:
This intensive 3-hour session will cover fundamental concepts of data analysis, visualization techniques, and practical applications using industry-standard tools. Whether you're a beginner or have some experience, this workshop will provide valuable skills for academic and professional success.

Topics Covered:
1. Introduction to Data Analysis
   • Understanding different types of data
   • Basic statistical concepts
   • Data cleaning and preparation techniques

2. Data Visualization Fundamentals
   • Principles of effective visualization
   • Choosing the right chart types
   • Color theory and design principles

3. Hands-on Practice with Real Data
   • Working with sample datasets
   • Creating charts and graphs
   • Interactive dashboards

4. Tools and Technologies
   • Excel for data analysis
   • Google Sheets for collaboration
   • Introduction to Python (pandas, matplotlib)
   • Tableau Public for advanced visualizations

5. Best Practices and Tips
   • Storytelling with data
   • Common pitfalls to avoid
   • Resources for continued learning

What You'll Learn:
• How to clean and prepare data for analysis
• Techniques for identifying patterns and trends
• Methods for creating compelling visualizations
• Tools for collaborative data work
• Best practices for presenting data insights

Prerequisites:
• Basic computer literacy
• No prior programming experience required
• Laptop recommended but not required (computers available)

Workshop Materials:
• All participants will receive digital resources
• Sample datasets for practice
• Step-by-step guides for tools
• Access to online learning resources

This workshop is perfect for:
• Students preparing for research projects
• Professionals looking to enhance their data skills
• Anyone interested in data-driven decision making
• Individuals seeking to improve their technical resume

Don't miss this opportunity to develop valuable skills that are increasingly in demand across all industries!''',
                'date': datetime.now().date() + timedelta(days=7),
                'time': '2:00 PM - 5:00 PM',
                'location': 'Innovation Hub, Technology Building, Room 201',
                'image': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'UPCOMING',
                'is_featured': False,
                'is_registration_open': True,
                'attendees': 75,
                'important_reminders': [
                    'Bring your laptop if you have one (not required)',
                    'Install Excel or Google Sheets beforehand',
                    'Arrive 10 minutes early for setup',
                    'Bring a notebook for taking notes',
                    'Download sample datasets from the provided link',
                    'Workshop materials will be shared via email'
                ]
            },
            {
                'title': 'Financial Literacy Seminar: Building Your Financial Future',
                'description': '''Gain essential knowledge on personal finance, investments, and financial planning to secure your financial future. This comprehensive seminar is designed to empower you with the knowledge and tools needed to make informed financial decisions.

Seminar Overview:
In today's complex financial landscape, understanding personal finance is more important than ever. This seminar will cover fundamental concepts and practical strategies to help you build wealth, manage debt, and achieve financial independence.

Topics Covered:

1. Personal Finance Fundamentals
   • Understanding income, expenses, and cash flow
   • Creating and maintaining a budget
   • Emergency fund planning
   • Debt management strategies

2. Banking and Credit
   • Choosing the right bank accounts
   • Understanding credit scores and reports
   • Credit card management
   • Building and maintaining good credit

3. Investment Basics
   • Understanding different investment types
   • Risk tolerance and investment goals
   • Diversification strategies
   • Long-term vs. short-term investing

4. Retirement Planning
   • Understanding retirement accounts
   • Compound interest and time value of money
   • Social security and pension plans
   • Creating a retirement strategy

5. Insurance and Protection
   • Types of insurance coverage
   • Health insurance basics
   • Life insurance considerations
   • Protecting your assets

6. Tax Planning
   • Understanding tax obligations
   • Tax-advantaged accounts
   • Deductions and credits
   • Tax planning strategies

Interactive Elements:
• Real-world case studies and examples
• Interactive budgeting exercises
• Q&A sessions with financial experts
• Personalized financial planning worksheets

Expert Speakers:
Our panel of financial experts includes:
• Certified Financial Planners
• Investment Advisors
• Tax Professionals
• Banking Representatives

What You'll Receive:
• Comprehensive financial planning workbook
• Budget templates and tools
• Investment resource guide
• Access to financial planning software
• Follow-up consultation opportunities

This seminar is perfect for:
• Students starting their financial journey
• Young professionals building wealth
• Anyone wanting to improve their financial literacy
• Individuals planning for major life events

Take control of your financial future and start building the life you want!''',
                'date': datetime.now().date() + timedelta(days=20),
                'time': '3:00 PM - 5:30 PM',
                'location': 'Business School, Room 104, Second Floor',
                'image': 'https://images.unsplash.com/photo-1579621970795-87facc2f976d?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'UPCOMING',
                'is_featured': False,
                'is_registration_open': True,
                'attendees': 120,
                'important_reminders': [
                    'Bring a calculator or smartphone for calculations',
                    'Come prepared with questions about your finances',
                    'Bring current financial statements if comfortable',
                    'Notebook and pen for taking notes',
                    'Business casual dress code',
                    'Refreshments will be provided'
                ]
            },
            {
                'title': 'Alumni Networking Night: Industry Connections',
                'description': '''Connect with successful JKUELC alumni across various industries during this special evening networking event. This is your opportunity to build professional relationships, learn from experienced professionals, and explore career opportunities.

Event Overview:
Networking is one of the most powerful tools for career advancement. This event brings together current students with accomplished alumni who have built successful careers in diverse fields. Whether you're exploring career options, seeking mentorship, or looking for internship opportunities, this event provides valuable connections.

Featured Alumni Sectors:
• Technology and Software Development
• Finance and Banking
• Healthcare and Medicine
• Education and Academia
• Entrepreneurship and Startups
• Government and Public Service
• Non-profit and Social Impact
• Creative Arts and Media

Event Format:
6:00 PM - 6:30 PM: Registration and Welcome
6:30 PM - 7:00 PM: Opening Remarks and Alumni Introductions
7:00 PM - 8:00 PM: Structured Networking Sessions
8:00 PM - 8:30 PM: Panel Discussion: "Career Paths and Opportunities"
8:30 PM - 9:00 PM: Open Networking and Refreshments

Networking Sessions:
• Speed networking with alumni
• Industry-specific breakout groups
• Resume review sessions
• Interview preparation tips
• Mentorship matching

Panel Discussion Topics:
• "Transitioning from Student to Professional"
• "Building Your Personal Brand"
• "Navigating Career Changes"
• "Work-Life Balance in Different Industries"

What to Bring:
• Business cards (if you have them)
• Updated resume
• Questions for alumni
• Professional attire
• Positive attitude and enthusiasm

Dress Code:
Business professional attire is recommended. This is a great opportunity to practice professional networking skills.

Benefits of Attending:
• Build your professional network
• Learn about different career paths
• Get advice from experienced professionals
• Discover internship and job opportunities
• Develop networking skills
• Gain industry insights

This event is open to all JKUELC members and students interested in professional development and networking opportunities.

Don't miss this chance to connect with our successful alumni and take your career to the next level!''',
                'date': datetime.now().date() + timedelta(days=45),
                'time': '6:00 PM - 9:00 PM',
                'location': 'JKU Faculty Club, Main Dining Hall',
                'image': 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?q=80&w=2787&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'UPCOMING',
                'is_featured': False,
                'is_registration_open': True,
                'attendees': 80,
                'important_reminders': [
                    'Business professional dress code required',
                    'Bring business cards if you have them',
                    'Prepare your elevator pitch',
                    'Bring copies of your resume',
                    'Arrive 15 minutes early for registration',
                    'Professional networking etiquette will be reviewed'
                ]
            },
            {
                'title': 'Leadership Book Club: "The 7 Habits of Highly Effective People"',
                'description': '''Join our weekly leadership book club where we discuss influential leadership books and apply their principles to our daily lives and leadership roles. This week we'll be diving deep into Stephen Covey's timeless classic "The 7 Habits of Highly Effective People."

Book Club Overview:
Reading and discussing leadership books is one of the most effective ways to develop leadership skills and gain new perspectives. Our book club provides a structured environment for meaningful discussions, practical applications, and peer learning.

This Week's Focus: "The 7 Habits of Highly Effective People"
Stephen Covey's masterpiece has influenced millions of leaders worldwide. We'll explore how these seven habits can transform your personal and professional effectiveness.

Discussion Topics:

1. Habit 1: Be Proactive
   • Understanding the circle of influence vs. circle of concern
   • Taking responsibility for your choices
   • Developing proactive language and mindset

2. Habit 2: Begin with the End in Mind
   • Creating personal mission statements
   • Setting clear goals and objectives
   • Understanding your values and principles

3. Habit 3: Put First Things First
   • Time management and prioritization
   • The importance vs. urgency matrix
   • Balancing different life roles

4. Habit 4: Think Win-Win
   • Abundance mentality
   • Seeking mutual benefit in relationships
   • Building trust and cooperation

5. Habit 5: Seek First to Understand, Then to Be Understood
   • Active listening skills
   • Empathetic communication
   • Understanding different perspectives

6. Habit 6: Synergize
   • Creative cooperation
   • Valuing differences
   • Building high-performing teams

7. Habit 7: Sharpen the Saw
   • Continuous self-renewal
   • Physical, mental, social, and spiritual development
   • Maintaining balance in life

Discussion Format:
• Brief overview of the week's habits
• Personal reflections and experiences
• Group discussion and insights
• Practical application exercises
• Action planning for the week ahead

What to Prepare:
• Read the assigned chapters (emailed in advance)
• Come with questions and insights
• Be ready to share personal experiences
• Bring a notebook for taking notes

Group Activities:
• Role-playing scenarios
• Personal mission statement writing
• Goal-setting exercises
• Habit tracking worksheets

This book club is perfect for:
• Current and aspiring leaders
• Anyone interested in personal development
• Students looking to improve their effectiveness
• Individuals seeking practical leadership tools

Join us for an engaging discussion and practical application of these timeless leadership principles!''',
                'date': datetime.now().date() + timedelta(days=3),
                'time': '5:30 PM - 7:00 PM',
                'location': 'University Library, Meeting Room 2, Third Floor',
                'image': 'https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?q=80&w=2874&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'UPCOMING',
                'is_featured': False,
                'is_registration_open': True,
                'attendees': 25,
                'important_reminders': [
                    'Read chapters 1-3 before the meeting',
                    'Bring your copy of the book if you have one',
                    'Come prepared with discussion questions',
                    'Bring a notebook for taking notes',
                    'Be ready to share personal experiences',
                    'Meeting materials will be provided'
                ]
            },
            {
                'title': 'Orientation for New Members: Welcome to JKUELC',
                'description': '''Welcome to the JKUELC family! This orientation event is designed to introduce new members to our organization, mission, activities, and the incredible opportunities that await you.

Orientation Overview:
Starting your journey with JKUELC is an exciting step toward personal and professional growth. This orientation will provide you with all the information you need to make the most of your membership and get involved in our vibrant community.

What You'll Learn:

1. JKUELC Mission and Vision
   • Our history and founding principles
   • Current organizational goals
   • How we serve the student community
   • Our commitment to leadership development

2. Organizational Structure
   • Executive committee roles and responsibilities
   • Committee structure and functions
   • How decisions are made
   • Communication channels and protocols

3. Membership Benefits
   • Access to exclusive events and workshops
   • Networking opportunities with professionals
   • Leadership development programs
   • Career guidance and mentorship
   • Community service opportunities

4. Getting Involved
   • Available committees and roles
   • Event planning and organization
   • Volunteer opportunities
   • Leadership positions and elections

5. Upcoming Events and Activities
   • Calendar of events for the semester
   • Registration processes
   • How to stay informed
   • Ways to contribute ideas

6. Communication and Resources
   • Social media platforms
   • Email lists and newsletters
   • Meeting schedules and locations
   • Contact information for leaders

7. Policies and Guidelines
   • Membership requirements
   • Attendance expectations
   • Code of conduct
   • Grievance procedures

Interactive Elements:
• Icebreaker activities to meet fellow members
• Q&A session with current leaders
• Small group discussions
• Tour of meeting spaces and facilities

What to Expect:
• Friendly, welcoming atmosphere
• Comprehensive information packet
• Opportunities to ask questions
• Networking with other new members
• Introduction to current leaders

Orientation Materials:
• Welcome packet with all important information
• Organization handbook
• Event calendar
• Contact directory
• Membership card

This orientation is mandatory for all new members and highly recommended for anyone who wants to learn more about our organization.

Join us and start your JKUELC journey on the right foot!''',
                'date': datetime.now().date() - timedelta(days=5),
                'time': '2:00 PM - 4:00 PM',
                'location': 'Student Center, Main Hall',
                'image': 'https://images.unsplash.com/photo-1546422401-68b415cbf8de?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'COMPLETED',
                'is_featured': False,
                'is_registration_open': False,
                'attendees': 35,
                'important_reminders': [
                    'Bring your student ID for verification',
                    'Come with questions about the organization',
                    'Be ready to introduce yourself to others',
                    'Bring a pen for taking notes',
                    'Orientation materials will be provided',
                    'Light refreshments will be served'
                ]
            },
            {
                'title': 'Leadership Development Workshop: Communication & Team Building',
                'description': '''Develop essential leadership skills through this intensive workshop focused on communication and team building. This hands-on workshop is designed to enhance your ability to lead effectively in any setting.

Workshop Overview:
Leadership is fundamentally about working with people - understanding them, communicating with them, and building strong teams. This workshop provides practical tools and techniques for becoming a more effective leader through improved communication and team-building skills.

Workshop Components:

1. Communication Skills for Leaders
   • Active listening techniques
   • Clear and concise messaging
   • Non-verbal communication
   • Difficult conversations
   • Feedback delivery and reception

2. Team Building Fundamentals
   • Understanding team dynamics
   • Building trust and rapport
   • Conflict resolution strategies
   • Motivating team members
   • Delegation and empowerment

3. Leadership Styles and Adaptability
   • Different leadership approaches
   • Situational leadership
   • Adapting to different personalities
   • Cultural sensitivity in leadership

4. Practical Applications
   • Role-playing scenarios
   • Team-building exercises
   • Communication drills
   • Real-world case studies

Interactive Activities:
• Communication role-plays
• Team-building games and exercises
• Leadership style assessments
• Group problem-solving challenges
• Peer feedback sessions

What You'll Learn:
• How to communicate more effectively as a leader
• Techniques for building strong, cohesive teams
• Strategies for handling difficult situations
• Tools for motivating and inspiring others
• Methods for resolving conflicts constructively

Workshop Materials:
• Leadership assessment tools
• Communication templates
• Team-building activity guides
• Reference materials and resources
• Certificate of completion

This workshop is perfect for:
• Current student organization leaders
• Aspiring leaders and managers
• Anyone working in team environments
• Individuals seeking to improve their interpersonal skills

Don't miss this opportunity to develop the communication and team-building skills that are essential for effective leadership!''',
                'date': datetime.now().date() - timedelta(days=10),
                'time': '9:00 AM - 1:00 PM',
                'location': 'JKU Conference Hall, Main Campus',
                'image': 'https://images.unsplash.com/photo-1558403194-611308249627?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'COMPLETED',
                'is_featured': False,
                'is_registration_open': False,
                'attendees': 60,
                'important_reminders': [
                    'Wear comfortable clothing for activities',
                    'Come with an open mind and positive attitude',
                    'Be ready to participate in group activities',
                    'Bring a notebook for taking notes',
                    'Workshop materials will be provided',
                    'Lunch will be served during the workshop'
                ]
            },
            {
                'title': 'Public Speaking Competition: Voices of Tomorrow',
                'description': '''Showcase your public speaking skills and compete with fellow students in our annual public speaking competition. This event celebrates eloquence, critical thinking, and the power of effective communication.

Competition Overview:
Public speaking is one of the most valuable skills for leadership and professional success. This competition provides a platform for students to demonstrate their speaking abilities while receiving valuable feedback from experienced judges.

Competition Format:

1. Preliminary Rounds
   • 3-5 minute prepared speeches
   • Topics provided in advance
   • Judging based on content, delivery, and impact
   • Top speakers advance to finals

2. Final Round
   • 5-7 minute prepared speeches
   • Impromptu speaking challenges
   • Comprehensive judging criteria
   • Awards and recognition

Speech Categories:
• Persuasive Speaking
• Informative Speaking
• Inspirational Speaking
• Current Events Analysis
• Personal Experience Stories

Judging Criteria:
• Content and Organization (30%)
• Delivery and Presentation (25%)
• Language and Style (20%)
• Audience Engagement (15%)
• Originality and Creativity (10%)

Prizes and Recognition:
• First Place: Trophy and certificate
• Second Place: Certificate and recognition
• Third Place: Certificate and recognition
• Best Delivery Award
• Most Creative Content Award
• Audience Choice Award

What to Prepare:
• Choose your speech topic from provided options
• Practice your delivery and timing
• Prepare for impromptu speaking challenges
• Review public speaking fundamentals

Workshop Sessions:
• Public speaking techniques
• Speech writing and organization
• Delivery and presentation skills
• Handling nervousness and anxiety
• Audience engagement strategies

This competition is open to all students and provides an excellent opportunity to:
• Develop public speaking confidence
• Receive professional feedback
• Network with other speakers
• Build your resume
• Gain recognition for your skills

Join us for an exciting celebration of communication and leadership!''',
                'date': datetime.now().date() - timedelta(days=20),
                'time': '3:00 PM - 6:00 PM',
                'location': 'Arts Auditorium, Performing Arts Center',
                'image': 'https://images.unsplash.com/photo-1563986768711-b3bde3dc821e?q=80&w=2848&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'COMPLETED',
                'is_featured': False,
                'is_registration_open': False,
                'attendees': 150,
                'important_reminders': [
                    'Submit your speech topic by the deadline',
                    'Practice your speech multiple times',
                    'Arrive 30 minutes early for registration',
                    'Bring a copy of your speech',
                    'Dress professionally for the competition',
                    'Be prepared for impromptu speaking'
                ]
            },
            {
                'title': 'Tech Innovation Summit: Future of Technology',
                'description': '''Explore the latest trends in technology and innovation at our comprehensive Tech Innovation Summit. This full-day event brings together tech leaders, entrepreneurs, researchers, and students to discuss the future of technology and its impact on society.

Summit Overview:
Technology is rapidly transforming every aspect of our lives. This summit provides a platform for exploring emerging technologies, discussing their implications, and networking with industry leaders and innovators.

Keynote Speakers:
• Dr. Sarah Chen - AI and Machine Learning Expert
• Marcus Rodriguez - Startup Founder and Tech Entrepreneur
• Prof. David Kim - Blockchain and Cryptocurrency Researcher
• Lisa Thompson - Sustainability in Technology Advocate

Panel Discussions:

1. "Artificial Intelligence and the Future of Work"
   • Impact of AI on various industries
   • Skills needed for the AI era
   • Ethical considerations in AI development
   • Preparing for AI-driven changes

2. "Startup Culture and Innovation"
   • Building successful tech startups
   • Funding and investment strategies
   • Innovation in established companies
   • Lessons from failed startups

3. "Sustainability in Technology"
   • Green computing and energy efficiency
   • Sustainable software development
   • Environmental impact of tech products
   • Circular economy in technology

4. "Cybersecurity in the Digital Age"
   • Current cybersecurity threats
   • Best practices for digital security
   • Privacy protection strategies
   • Future of cybersecurity

Workshop Sessions:
• Introduction to Machine Learning
• Web Development Fundamentals
• Mobile App Development
• Data Science Basics
• Cloud Computing Overview
• Cybersecurity Fundamentals

Startup Showcase:
• Presentations from local tech startups
• Demo of innovative products
• Networking with entrepreneurs
• Investment opportunities

Networking Opportunities:
• Speed networking sessions
• Industry-specific breakout groups
• Mentorship matching
• Career fair with tech companies

What You'll Gain:
• Insights into emerging technologies
• Networking with tech professionals
• Hands-on experience with new tools
• Career guidance in tech fields
• Understanding of industry trends

This summit is perfect for:
• Students interested in technology careers
• Professionals looking to stay current
• Entrepreneurs seeking innovation insights
• Anyone curious about the future of tech

Join us for a day of innovation, learning, and networking in the exciting world of technology!''',
                'date': datetime.now().date() + timedelta(days=60),
                'time': '10:00 AM - 6:00 PM',
                'location': 'Innovation Center, Technology Campus',
                'image': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3',
                'status': 'UPCOMING',
                'is_featured': True,
                'is_registration_open': True,
                'attendees': 200,
                'important_reminders': [
                    'Bring your laptop for hands-on workshops',
                    'Download required software beforehand',
                    'Come prepared with questions for speakers',
                    'Bring business cards for networking',
                    'Dress code: Business casual',
                    'Lunch and refreshments will be provided'
                ]
            },
        ]

        # Create events
        created_count = 0
        for event_data in sample_events:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults={
                    'description': event_data['description'],
                    'date': event_data['date'],
                    'time': event_data['time'],
                    'location': event_data['location'],
                    'image': event_data['image'],
                    'status': event_data['status'],
                    'is_featured': event_data['is_featured'],
                    'is_registration_open': event_data['is_registration_open'],
                    'attendees': event_data['attendees'],
                    'important_reminders': event_data.get('important_reminders', []),
                    'created_by': user,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created event: {event.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample events!')
        ) 