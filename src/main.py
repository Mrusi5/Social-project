from fastapi import Depends, FastAPI, Request
from sqlalchemy import desc, select
from src.database import Post, get_async_session
from src.auth.routers import is_authenticated
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.jinja_utils import create_jinja2_environment
from src.auth.routers import router as auth_router
from src.post.routers import router as post_router
from sqlalchemy.ext.asyncio import AsyncSession



app = FastAPI(
    title = "Social"
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")
templates.env = create_jinja2_environment()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

def add_auth_context(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_auth_info(request: Request, call_next):
        is_authenticated = is_authenticated(request)
        request.state.is_authenticated = is_authenticated
        
        response = await call_next(request)
        return response







# base шаблон для навигации 
@app.get("/base", response_class=HTMLResponse)
async def base(request: Request):
    context = {
        'is_authenticated': is_authenticated(request),
        'request': request
    }
    return templates.TemplateResponse('base.html', context)



# Домашняя страница
@app.get("/home", response_class=HTMLResponse)
async def home(
    request: Request, 
    session: AsyncSession = Depends(get_async_session)
    ):
    query = select(Post).order_by(desc(Post.created_at))
    result = await session.execute(query)
    posts = result.scalars().all()
    context = {
        'is_authenticated': is_authenticated(request),
        'request': request,
        'posts' : posts
    }
    return templates.TemplateResponse("home.html", context)


app.include_router(auth_router)
app.include_router(post_router)