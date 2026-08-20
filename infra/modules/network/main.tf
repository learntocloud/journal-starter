resource "aws_vpc" "journal-api-eks-vpc" {
  cidr_block = var.vpc_cidr_block
}

#Public subnets
resource "aws_subnet" "journal-api-eks-vpc-PublicSubnet01" {
  vpc_id                  = aws_vpc.journal-api-eks-vpc.id
  cidr_block              = var.public_subnets_cidr_blocks[0]
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true

}

resource "aws_subnet" "journal-api-eks-vpc-PublicSubnet02" {
  vpc_id                  = aws_vpc.journal-api-eks-vpc.id
  cidr_block              = var.public_subnets_cidr_blocks[1]
  availability_zone       = var.availability_zones[1]
  map_public_ip_on_launch = true
}

#Private subnets
resource "aws_subnet" "journal-api-eks-vpc-PrivateSubnet01" {
  vpc_id            = aws_vpc.journal-api-eks-vpc.id
  cidr_block        = var.private_subnets_cidr_blocks[0]
  availability_zone = var.availability_zones[0]
}

resource "aws_subnet" "journal-api-eks-vpc-PrivateSubnet02" {
  vpc_id            = aws_vpc.journal-api-eks-vpc.id
  cidr_block        = var.private_subnets_cidr_blocks[1]
  availability_zone = var.availability_zones[1]
}

#Internet Gateway
resource "aws_internet_gateway" "journal-api-eks-vpc-igw" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id
}

#Elastic IPs for NAT Gateways
resource "aws_eip" "journal-api-eks-vpc-NatGatewayEIPAZ1" {
  domain = "vpc"
}

resource "aws_eip" "journal-api-eks-vpc-NatGatewayEIPAZ2" {
  domain = "vpc"
}

#Nat Gateway
resource "aws_nat_gateway" "journal-api-eks-vpc-NatGatewayAZ1" {
  allocation_id = aws_eip.journal-api-eks-vpc-NatGatewayEIPAZ1.id
  subnet_id     = aws_subnet.journal-api-eks-vpc-PublicSubnet01.id
}

resource "aws_nat_gateway" "journal-api-eks-vpc-NatGatewayAZ2" {
  allocation_id = aws_eip.journal-api-eks-vpc-NatGatewayEIPAZ2.id
  subnet_id     = aws_subnet.journal-api-eks-vpc-PublicSubnet02.id
}

# Routes tables / associations
resource "aws_route_table" "Public_Subnets" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.journal-api-eks-vpc-igw.id
  }
}

resource "aws_route_table_association" "Public_Subnet_1" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PublicSubnet01.id
  route_table_id = aws_route_table.Public_Subnets.id
}

resource "aws_route_table_association" "Public_Subnet_2" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PublicSubnet02.id
  route_table_id = aws_route_table.Public_Subnets.id
}

resource "aws_route_table" "Private_Subnet_AZ1" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.journal-api-eks-vpc-NatGatewayAZ1.id
  }
}

resource "aws_route_table" "Private_Subnet_AZ2" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.journal-api-eks-vpc-NatGatewayAZ2.id
  }
}

resource "aws_route_table_association" "Private_Subnet_1" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PrivateSubnet01.id
  route_table_id = aws_route_table.Private_Subnet_AZ1.id
}

resource "aws_route_table_association" "Private_Subnet_2" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PrivateSubnet02.id
  route_table_id = aws_route_table.Private_Subnet_AZ2.id
}
