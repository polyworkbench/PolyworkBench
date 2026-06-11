# Cloud Computing Fundamentals - Training Slides

---

## Slide 1: Course Introduction

### Welcome to Cloud Computing Fundamentals

**Course Duration**: 2 days (16 hours)
**Target Audience**: IT professionals transitioning to cloud
**Prerequisites**: Basic networking and OS knowledge

This course covers:
- Cloud computing concepts and terminology
- Service models (IaaS, PaaS, SaaS)
- Deployment models
- Core cloud services
- Security best practices
- Hands-on labs with AWS and Alibaba Cloud

---

## Slide 2: What is Cloud Computing?

### Definition

Cloud computing is the on-demand delivery of IT resources over the internet with pay-as-you-go pricing. Instead of buying, owning, and maintaining physical data centers and servers, you can access technology services on an as-needed basis.

### Key Characteristics (NIST Definition)
- **On-demand self-service**: Provision resources without human interaction
- **Broad network access**: Available over the network via standard mechanisms
- **Resource pooling**: Multi-tenant model with dynamic resource assignment
- **Rapid elasticity**: Scale up/down quickly based on demand
- **Measured service**: Pay only for what you use

---

## Slide 3: Cloud Service Models

### IaaS (Infrastructure as a Service)
- Virtual machines, storage, networking
- Examples: AWS EC2, Alibaba Cloud ECS, Azure VMs
- User manages: OS, middleware, applications
- Provider manages: Hardware, virtualization, networking

### PaaS (Platform as a Service)
- Development platforms and tools
- Examples: AWS Elastic Beanstalk, Alibaba Cloud Web App Service
- User manages: Applications and data
- Provider manages: Runtime, OS, infrastructure

### SaaS (Software as a Service)
- Complete applications delivered over internet
- Examples: Gmail, Salesforce, Office 365
- User manages: Data and access
- Provider manages: Everything else

---

## Slide 4: Deployment Models

### Public Cloud
- Owned and operated by third-party provider
- Shared infrastructure, lowest cost
- Best for: Variable workloads, testing, web applications

### Private Cloud
- Dedicated infrastructure for single organization
- Higher security and control
- Best for: Regulated industries, sensitive data

### Hybrid Cloud
- Combination of public and private clouds
- Data and applications can move between environments
- Best for: Burst capacity, gradual migration

### Multi-Cloud
- Using services from multiple cloud providers
- Avoid vendor lock-in
- Best for: Best-of-breed services, disaster recovery

---

## Slide 5: Compute Services

### Virtual Machines
- **AWS EC2**: Scalable virtual servers with 500+ instance types
- **Alibaba Cloud ECS**: Elastic compute with GPU/FPGA options
- Instance families: General purpose, Compute-optimized, Memory-optimized, Storage-optimized

### Containers
- **AWS ECS/EKS**: Container orchestration (Docker/Kubernetes)
- **Alibaba Cloud ACK**: Managed Kubernetes service
- Benefits: Portability, efficiency, microservices architecture

### Serverless
- **AWS Lambda**: Run code without provisioning servers
- **Alibaba Cloud Function Compute**: Event-driven serverless
- Pay per execution, auto-scaling to zero

---

## Slide 6: Storage Services

### Object Storage
- **AWS S3**: Virtually unlimited storage, 99.999999999% durability
- **Alibaba Cloud OSS**: Object Storage Service
- Use cases: Backups, static websites, data lakes

### Block Storage
- **AWS EBS**: Persistent block storage for EC2
- **Alibaba Cloud Block Storage**: High-performance disks
- Types: SSD (gp3, io2), HDD (st1, sc1)

### File Storage
- **AWS EFS**: Managed NFS file system
- **Alibaba Cloud NAS**: Network Attached Storage
- Use cases: Shared file systems, content management

### Storage Classes and Cost Optimization
- Hot storage: Frequent access (Standard)
- Warm storage: Infrequent access (IA)
- Cold storage: Archive (Glacier, Archive)

---

## Slide 7: Database Services

### Relational Databases
- **AWS RDS**: MySQL, PostgreSQL, Oracle, SQL Server
- **Alibaba Cloud ApsaraDB**: RDS with automated management
- Features: Auto backups, read replicas, multi-AZ deployment

### NoSQL Databases
- **AWS DynamoDB**: Key-value and document database
- **Alibaba Cloud Tablestore**: Wide-column NoSQL
- Use cases: Gaming, IoT, real-time applications

### In-Memory Databases
- **AWS ElastiCache**: Redis and Memcached
- **Alibaba Cloud Tair**: Enhanced Redis
- Use cases: Caching, session management, leaderboards

### Data Warehouses
- **AWS Redshift**: Petabyte-scale data warehouse
- **Alibaba Cloud MaxCompute**: Big data analytics platform
- Use cases: Business intelligence, analytics

---

## Slide 8: Networking Services

### Virtual Private Cloud (VPC)
- Isolated network environment in the cloud
- Subnets, route tables, internet gateways
- Security groups and network ACLs

### Content Delivery Network (CDN)
- **AWS CloudFront**: Global edge network
- **Alibaba Cloud CDN**: 2800+ edge nodes worldwide
- Reduces latency for end users

### Load Balancing
- **AWS ALB/NLB**: Application and Network load balancers
- **Alibaba Cloud SLB**: Server Load Balancer
- Distribute traffic across multiple targets

### DNS Services
- **AWS Route 53**: Scalable DNS web service
- **Alibaba Cloud DNS**: Intelligent DNS resolution

---

## Slide 9: Security in the Cloud

### Shared Responsibility Model
- **Provider responsibility**: Security OF the cloud (infrastructure)
- **Customer responsibility**: Security IN the cloud (data, access)

### Identity and Access Management (IAM)
- Users, groups, roles, policies
- Principle of least privilege
- Multi-factor authentication (MFA)

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Key management services (AWS KMS, Alibaba Cloud KMS)

### Compliance
- SOC 2, ISO 27001, PCI DSS, HIPAA
- Regional compliance: GDPR (Europe), PDPA (Southeast Asia)
- Shared audit and compliance reports

---

## Slide 10: Serverless Architecture

### What is Serverless?
- No server management required
- Automatic scaling (including to zero)
- Pay per request/execution time
- Built-in high availability

### Common Serverless Patterns
1. **API Backend**: API Gateway + Lambda/Function Compute
2. **Event Processing**: S3/OSS trigger → Function → Database
3. **Scheduled Tasks**: CloudWatch/Timer trigger → Function
4. **Stream Processing**: Kinesis/DataHub → Function → Output

### When to Use Serverless
- ✅ Variable/unpredictable workloads
- ✅ Microservices and event-driven architectures
- ✅ Rapid prototyping
- ❌ Long-running processes (>15 min)
- ❌ Predictable, steady-state workloads

---

## Slide 11: Cost Management

### Pricing Models
- **On-Demand**: Pay by hour/second, no commitment
- **Reserved/Savings Plans**: 1-3 year commitment, up to 72% savings
- **Spot/Preemptible**: Up to 90% discount, can be interrupted

### Cost Optimization Strategies
1. Right-sizing: Match instance to workload
2. Auto-scaling: Scale based on demand
3. Storage tiering: Move data to cheaper tiers
4. Reserved capacity for baseline workloads
5. Regular review with cost analysis tools

### Tools
- **AWS Cost Explorer / Alibaba Cloud Bill Management**
- **AWS Trusted Advisor / Alibaba Cloud Advisor**
- Budgets and alerts

---

## Slide 12: Migration and Best Practices

### Cloud Migration Strategies (6 Rs)
1. **Rehost** (Lift and shift)
2. **Replatform** (Lift and optimize)
3. **Repurchase** (Move to SaaS)
4. **Refactor** (Re-architect for cloud-native)
5. **Retire** (Decommission)
6. **Retain** (Keep on-premises)

### Architecture Best Practices
- Design for failure (assume everything fails)
- Decouple components (use queues, events)
- Implement elasticity (auto-scaling)
- Think parallel (distribute workloads)
- Keep dynamic data close to compute
- Use managed services when possible

### Well-Architected Framework Pillars
1. Operational Excellence
2. Security
3. Reliability
4. Performance Efficiency
5. Cost Optimization
6. Sustainability
