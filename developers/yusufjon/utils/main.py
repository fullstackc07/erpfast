from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func
from typing import Optional, List
from databases.main import Base, get_db, ActiveSession, engine
from security.auth import get_current_active_user
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, DateTime, Time, Text, Boolean
from sqlalchemy.orm import relationship, joinedload, subqueryload, contains_eager, Session
import math
from . filtration import looking_for
from developers.yusufjon.schemas.user import NewUser
from pydantic import BaseModel, validator

