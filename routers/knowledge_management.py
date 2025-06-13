from fastapi import APIRouter, Depends, HTTPException, Body, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import random
import uuid
from .auth import get_current_user

# Create router for Knowledge Management
router = APIRouter(prefix="/api/documents", tags=["documents"])

# Models for document management
class DocumentMetadata(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    facility_id: Optional[str] = None
    facility_name: Optional[str] = None
    author: str
    upload_date: datetime
    last_modified: datetime
    file_type: str
    file_size: int  # Size in bytes
    file_path: str
    tags: List[str] = []
    version: str = "1.0"

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class DocumentUploadRequest(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    facility_id: Optional[str] = None
    tags: List[str] = []

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    facility_id: Optional[str] = None
    tags: Optional[List[str]] = None

# Sample document categories
document_categories = [
    "Safety Inspection",
    "Environmental",
    "Technical",
    "Monitoring",
    "Emergency",
    "Compliance",
    "Community",
    "Design",
    "Operations",
    "Maintenance"
]

# Sample facilities
sample_facilities = {
    "FAC001": "North Basin Facility",
    "FAC002": "South Basin Facility",
    "FAC003": "East Basin Facility",
    "FAC004": "West Basin Facility"
}

# Sample file types
file_types = ["PDF", "DOCX", "XLSX", "PPTX", "JPG", "PNG", "CSV", "TXT"]

# Sample authors
sample_authors = [
    "John Smith",
    "Maria Rodriguez",
    "David Chen",
    "Sarah Johnson",
    "Robert Williams",
    "Jennifer Lee",
    "Michael Brown",
    "Thomas Anderson"
]

# Sample document data
sample_documents = [
    {
        "id": "DOC001",
        "title": "Tailings Dam Safety Inspection Report - Q1 2025",
        "description": "Quarterly safety inspection report for the North Basin tailings facility",
        "category": "Safety Inspection",
        "facility_id": "FAC001",
        "facility_name": "North Basin Facility",
        "author": "John Smith",
        "upload_date": datetime(2025, 3, 15),
        "last_modified": datetime(2025, 3, 15),
        "file_type": "PDF",
        "file_size": 4200000,  # 4.2 MB
        "file_path": "/storage/documents/DOC001.pdf",
        "tags": ["inspection", "safety", "quarterly", "2025"],
        "version": "1.0"
    },
    {
        "id": "DOC002",
        "title": "Environmental Impact Assessment - South Basin Expansion",
        "description": "Environmental impact assessment for the proposed expansion of the South Basin facility",
        "category": "Environmental",
        "facility_id": "FAC002",
        "facility_name": "South Basin Facility",
        "author": "Maria Rodriguez",
        "upload_date": datetime(2025, 2, 10),
        "last_modified": datetime(2025, 2, 15),
        "file_type": "PDF",
        "file_size": 12800000,  # 12.8 MB
        "file_path": "/storage/documents/DOC002.pdf",
        "tags": ["environmental", "assessment", "expansion", "impact"],
        "version": "1.2"
    },
    {
        "id": "DOC003",
        "title": "Geotechnical Analysis Report - East Dam",
        "description": "Detailed geotechnical analysis of the East Basin dam structure",
        "category": "Technical",
        "facility_id": "FAC003",
        "facility_name": "East Basin Facility",
        "author": "David Chen",
        "upload_date": datetime(2025, 1, 22),
        "last_modified": datetime(2025, 1, 22),
        "file_type": "PDF",
        "file_size": 8500000,  # 8.5 MB
        "file_path": "/storage/documents/DOC003.pdf",
        "tags": ["geotechnical", "analysis", "dam", "structure"],
        "version": "1.0"
    },
    {
        "id": "DOC004",
        "title": "Water Quality Monitoring Results - Q4 2024",
        "description": "Quarterly water quality monitoring results for the North Basin facility",
        "category": "Monitoring",
        "facility_id": "FAC001",
        "facility_name": "North Basin Facility",
        "author": "Sarah Johnson",
        "upload_date": datetime(2025, 1, 5),
        "last_modified": datetime(2025, 1, 10),
        "file_type": "XLSX",
        "file_size": 3100000,  # 3.1 MB
        "file_path": "/storage/documents/DOC004.xlsx",
        "tags": ["water quality", "monitoring", "quarterly", "2024"],
        "version": "1.1"
    },
    {
        "id": "DOC005",
        "title": "Emergency Response Plan - 2025 Update",
        "description": "Updated emergency response plan for all tailings facilities",
        "category": "Emergency",
        "facility_id": None,
        "facility_name": "All Facilities",
        "author": "Robert Williams",
        "upload_date": datetime(2025, 1, 1),
        "last_modified": datetime(2025, 1, 1),
        "file_type": "PDF",
        "file_size": 5700000,  # 5.7 MB
        "file_path": "/storage/documents/DOC005.pdf",
        "tags": ["emergency", "response", "plan", "2025"],
        "version": "2.0"
    },
    {
        "id": "DOC006",
        "title": "Regulatory Compliance Checklist",
        "description": "Checklist for ensuring compliance with regulatory requirements",
        "category": "Compliance",
        "facility_id": None,
        "facility_name": "All Facilities",
        "author": "Jennifer Lee",
        "upload_date": datetime(2024, 12, 15),
        "last_modified": datetime(2024, 12, 15),
        "file_type": "XLSX",
        "file_size": 1200000,  # 1.2 MB
        "file_path": "/storage/documents/DOC006.xlsx",
        "tags": ["regulatory", "compliance", "checklist"],
        "version": "1.0"
    },
    {
        "id": "DOC007",
        "title": "Stakeholder Engagement Report - 2024",
        "description": "Annual report on stakeholder engagement activities",
        "category": "Community",
        "facility_id": None,
        "facility_name": "All Facilities",
        "author": "Michael Brown",
        "upload_date": datetime(2024, 12, 10),
        "last_modified": datetime(2024, 12, 10),
        "file_type": "PDF",
        "file_size": 6300000,  # 6.3 MB
        "file_path": "/storage/documents/DOC007.pdf",
        "tags": ["stakeholder", "engagement", "community", "2024"],
        "version": "1.0"
    },
    {
        "id": "DOC008",
        "title": "Tailings Storage Facility Design Specifications",
        "description": "Technical design specifications for the West Basin tailings storage facility",
        "category": "Design",
        "facility_id": "FAC004",
        "facility_name": "West Basin Facility",
        "author": "Thomas Anderson",
        "upload_date": datetime(2024, 11, 28),
        "last_modified": datetime(2024, 11, 30),
        "file_type": "PDF",
        "file_size": 15400000,  # 15.4 MB
        "file_path": "/storage/documents/DOC008.pdf",
        "tags": ["design", "specifications", "technical", "storage"],
        "version": "1.3"
    }
]

# Generate more sample documents
def generate_more_documents(count: int = 20):
    documents = sample_documents.copy()
    
    for i in range(len(documents), len(documents) + count):
        # Generate random document data
        doc_id = f"DOC{i+1:03d}"
        category = random.choice(document_categories)
        
        # Decide if document is facility-specific or for all facilities
        if random.random() < 0.7:  # 70% chance of being facility-specific
            facility_id = random.choice(list(sample_facilities.keys()))
            facility_name = sample_facilities[facility_id]
        else:
            facility_id = None
            facility_name = "All Facilities"
        
        # Generate random dates within the past year
        days_ago = random.randint(1, 365)
        upload_date = datetime.now() - datetime.timedelta(days=days_ago)
        
        # 20% chance of having been modified after upload
        if random.random() < 0.2:
            mod_days_ago = random.randint(1, days_ago)
            last_modified = datetime.now() - datetime.timedelta(days=mod_days_ago)
        else:
            last_modified = upload_date
        
        # Generate random file size between 500KB and 20MB
        file_size = random.randint(500000, 20000000)
        
        # Generate random title based on category
        if category == "Safety Inspection":
            title = f"Safety Inspection Report - {facility_name} - {upload_date.strftime('%b %Y')}"
            tags = ["safety", "inspection", upload_date.strftime("%Y")]
        elif category == "Environmental":
            title = f"Environmental Monitoring Report - {facility_name} - {upload_date.strftime('%b %Y')}"
            tags = ["environmental", "monitoring", upload_date.strftime("%Y")]
        elif category == "Technical":
            title = f"Technical Assessment - {facility_name} - {upload_date.strftime('%b %Y')}"
            tags = ["technical", "assessment", upload_date.strftime("%Y")]
        elif category == "Monitoring":
            title = f"Monitoring Data Summary - {facility_name} - {upload_date.strftime('%b %Y')}"
            tags = ["monitoring", "data", upload_date.strftime("%Y")]
        elif category == "Emergency":
            title = f"Emergency Procedure Update - {upload_date.strftime('%b %Y')}"
            tags = ["emergency", "procedure", upload_date.strftime("%Y")]
        elif category == "Compliance":
            title = f"Regulatory Compliance Report - {upload_date.strftime('%b %Y')}"
            tags = ["compliance", "regulatory", upload_date.strftime("%Y")]
        elif category == "Community":
            title = f"Community Engagement Summary - {upload_date.strftime('%b %Y')}"
            tags = ["community", "engagement", upload_date.strftime("%Y")]
        elif category == "Design":
            title = f"Design Modification - {facility_name} - {upload_date.strftime('%b %Y')}"
            tags = ["design", "modification", upload_date.strftime("%Y")]
        elif category == "Operations":
            title = f"Operations Manual Update - {facility_name} - {upload_date.strftime('%b %Y')}"
            tags = ["operations", "manual", upload_date.strftime("%Y")]
        else:
            title = f"Maintenance Schedule - {facility_name} - {upload_date.strftime('%b %Y')}"
            tags = ["maintenance", "schedule", upload_date.strftime("%Y")]
        
        # Add random tags
        if random.random() < 0.5:
            tags.append("important")
        if random.random() < 0.3:
            tags.append("review-required")
        
        # Generate document
        document = {
            "id": doc_id,
            "title": title,
            "description": f"Document description for {title}",
            "category": category,
            "facility_id": facility_id,
            "facility_name": facility_name,
            "author": random.choice(sample_authors),
            "upload_date": upload_date,
            "last_modified": last_modified,
            "file_type": random.choice(file_types),
            "file_size": file_size,
            "file_path": f"/storage/documents/{doc_id}.{random.choice(file_types).lower()}",
            "tags": tags,
            "version": f"1.{random.randint(0, 5)}"
        }
        
        documents.append(document)
    
    return documents

# API Endpoints

@router.get("/categories", response_model=List[str])
async def get_document_categories(current_user: dict = Depends(get_current_user)):
    """Get list of document categories"""
    return document_categories

@router.get("/facilities", response_model=Dict[str, str])
async def get_document_facilities(current_user: dict = Depends(get_current_user)):
    """Get list of facilities for document filtering"""
    return sample_facilities

@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    facility_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("upload_date"),
    sort_order: str = Query("desc"),
    current_user: dict = Depends(get_current_user)
):
    """
    List documents with pagination, filtering, and sorting
    """
    # Get all documents (in a real implementation, this would query a database)
    all_documents = sample_documents
    
    # Apply filters
    filtered_docs = all_documents
    
    if category:
        filtered_docs = [doc for doc in filtered_docs if doc["category"] == category]
    
    if facility_id:
        filtered_docs = [doc for doc in filtered_docs if doc["facility_id"] == facility_id]
    
    if search:
        search_lower = search.lower()
        filtered_docs = [
            doc for doc in filtered_docs 
            if search_lower in doc["title"].lower() 
            or (doc["description"] and search_lower in doc["description"].lower())
            or any(search_lower in tag.lower() for tag in doc["tags"])
        ]
    
    # Sort documents
    if sort_by == "title":
        filtered_docs.sort(key=lambda x: x["title"], reverse=(sort_order == "desc"))
    elif sort_by == "category":
        filtered_docs.sort(key=lambda x: x["category"], reverse=(sort_order == "desc"))
    elif sort_by == "file_size":
        filtered_docs.sort(key=lambda x: x["file_size"], reverse=(sort_order == "desc"))
    else:  # Default to upload_date
        filtered_docs.sort(key=lambda x: x["upload_date"], reverse=(sort_order == "desc"))
    
    # Calculate pagination
    total_count = len(filtered_docs)
    total_pages = (total_count + page_size - 1) // page_size
    
    # Adjust page if out of bounds
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Get documents for current page
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_count)
    page_documents = filtered_docs[start_idx:end_idx]
    
    # Convert to DocumentMetadata objects
    document_objects = [DocumentMetadata(**doc) for doc in page_documents]
    
    return {
        "documents": document_objects,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get document metadata by ID"""
    for doc in sample_documents:
        if doc["id"] == document_id:
            return DocumentMetadata(**doc)
    
    raise HTTPException(status_code=404, detail="Document not found")

@router.post("", response_model=DocumentMetadata)
async def upload_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    facility_id: Optional[str] = Form(None),
    tags: str = Form(""),  # Comma-separated tags
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a new document"""
    # Validate category
    if category not in document_categories:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Validate facility_id if provided
    if facility_id and facility_id not in sample_facilities:
        raise HTTPException(status_code=400, detail="Invalid facility ID")
    
    # Process tags
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    # Generate a new document ID
    doc_id = f"DOC{len(sample_documents) + 1:03d}"
    
    # Get file size and type
    file_content = await file.read()
    file_size = len(file_content)
    
    # Extract file extension
    file_ext = os.path.splitext(file.filename)[1].lstrip(".").upper()
    if not file_ext:
        file_ext = "BIN"  # Default for files without extension
    
    # In a real implementation, save the file to storage
    file_path = f"/storage/documents/{doc_id}.{file_ext.lower()}"
    
    # Create new document metadata
    now = datetime.now()
    new_doc = {
        "id": doc_id,
        "title": title,
        "description": description,
        "category": category,
        "facility_id": facility_id,
        "facility_name": sample_facilities.get(facility_id, "All Facilities") if facility_id else "All Facilities",
        "author": current_user["username"],
        "upload_date": now,
        "last_modified": now,
        "file_type": file_ext,
        "file_size": file_size,
        "file_path": file_path,
        "tags": tag_list,
        "version": "1.0"
    }
    
    # In a real implementation, save to database
    sample_documents.append(new_doc)
    
    return DocumentMetadata(**new_doc)

@router.put("/{document_id}", response_model=DocumentMetadata)
async def update_document(
    document_id: str,
    update_data: DocumentUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update document metadata"""
    # Find the document
    for i, doc in enumerate(sample_documents):
        if doc["id"] == document_id:
            # Validate category if provided
            if update_data.category and update_data.category not in document_categories:
                raise HTTPException(status_code=400, detail="Invalid category")
            
            # Validate facility_id if provided
            if update_data.facility_id and update_data.facility_id not in sample_facilities:
                raise HTTPException(status_code=400, detail="Invalid facility ID")
            
            # Update fields if provided
            if update_data.title:
                doc["title"] = update_data.title
            
            if update_data.description is not None:  # Allow empty string to clear description
                doc["description"] = update_data.description
            
            if update_data.category:
                doc["category"] = update_data.category
            
            if update_data.facility_id is not None:  # Allow None to set to All Facilities
                doc["facility_id"] = update_data.facility_id
                doc["facility_name"] = sample_facilities.get(update_data.facility_id, "All Facilities") if update_data.facility_id else "All Facilities"
            
            if update_data.tags is not None:
                doc["tags"] = update_data.tags
            
            # Update last_modified timestamp
            doc["last_modified"] = datetime.now()
            
            # Increment version
            version_parts = doc["version"].split(".")
            if len(version_parts) == 2:
                major, minor = version_parts
                doc["version"] = f"{major}.{int(minor) + 1}"
            
            # In a real implementation, update in database
            sample_documents[i] = doc
            
            return DocumentMetadata(**doc)
    
    raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document"""
    # Find the document
    for i, doc in enumerate(sample_documents):
        if doc["id"] == document_id:
            # In a real implementation, delete file from storage
            
            # Remove from list
            sample_documents.pop(i)
            return
    
    raise HTTPException(status_code=404, detail="Document not found")

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download a document file"""
    # Find the document
    for doc in sample_documents:
        if doc["id"] == document_id:
            # In a real implementation, this would return the actual file
            # For this mock implementation, we'll raise an exception
            raise HTTPException(
                status_code=501, 
                detail="Document download not implemented in mock API. In a real implementation, this would return the file."
            )
    
    raise HTTPException(status_code=404, detail="Document not found")

@router.post("/{document_id}/version", response_model=DocumentMetadata)
async def upload_new_version(
    document_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a new version of an existing document"""
    # Find the document
    for i, doc in enumerate(sample_documents):
        if doc["id"] == document_id:
            # Get file size
            file_content = await file.read()
            file_size = len(file_content)
            
            # Extract file extension
            file_ext = os.path.splitext(file.filename)[1].lstrip(".").upper()
            if not file_ext:
                file_ext = "BIN"  # Default for files without extension
            
            # In a real implementation, save the file to storage
            file_path = f"/storage/documents/{doc_id}.{file_ext.lower()}"
            
            # Update document metadata
            doc["last_modified"] = datetime.now()
            doc["file_size"] = file_size
            doc["file_type"] = file_ext
            doc["file_path"] = file_path
            
            # Increment version
            version_parts = doc["version"].split(".")
            if len(version_parts) == 2:
                major, minor = version_parts
                doc["version"] = f"{major}.{int(minor) + 1}"
            
            # In a real implementation, update in database
            sample_documents[i] = doc
            
            return DocumentMetadata(**doc)
    
    raise HTTPException(status_code=404, detail="Document not found")
