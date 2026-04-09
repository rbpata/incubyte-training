import {
    createContext,
    useContext,
    useReducer,
    useCallback,
    useMemo
} from 'react';
import type {AuthUser, TokenResponse} from '../types/index';

interface AuthState {
    accessToken: string;
    refreshToken: string;
    user: AuthUser | null;
    isLoading: boolean;
    error: string | null;
}

export type AuthAction =
    | {type: 'LOGIN_START'}
    | {type: 'LOGIN_SUCCESS'; payload: {tokens: TokenResponse; user: AuthUser}}
    | {type: 'LOGIN_FAILURE'; payload: string}
    | {type: 'LOGOUT'}
    | {type: 'SET_USER'; payload: AuthUser}
    | {type: 'REFRESH_SUCCESS'; payload: TokenResponse}
    | {type: 'CLEAR_ERROR'}
    | {
          type: 'RESTORE_TOKENS';
          payload: {accessToken: string; refreshToken: string};
      };

interface AuthContextType extends AuthState {
    dispatch: (action: AuthAction) => void;
    login: (tokens: TokenResponse, user: AuthUser) => void;
    logout: () => void;
    setUser: (user: AuthUser) => void;
    refreshTokens: (tokens: TokenResponse) => void;
    clearError: () => void;
    restoreTokens: (accessToken: string, refreshToken: string) => void;
    isLoggedIn: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const initialState: AuthState = {
    accessToken: '',
    refreshToken: '',
    user: null,
    isLoading: false,
    error: null
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
    switch (action.type) {
        case 'LOGIN_START':
            return {...state, isLoading: true, error: null};

        case 'LOGIN_SUCCESS':
            return {
                ...state,
                accessToken: action.payload.tokens.access_token,
                refreshToken: action.payload.tokens.refresh_token,
                user: action.payload.user,
                isLoading: false,
                error: null
            };

        case 'LOGIN_FAILURE':
            return {...state, isLoading: false, error: action.payload};

        case 'LOGOUT':
            return {...initialState};

        case 'SET_USER':
            return {...state, user: action.payload};

        case 'REFRESH_SUCCESS':
            return {
                ...state,
                accessToken: action.payload.access_token,
                refreshToken: action.payload.refresh_token
            };

        case 'CLEAR_ERROR':
            return {...state, error: null};

        case 'RESTORE_TOKENS':
            return {
                ...state,
                accessToken: action.payload.accessToken,
                refreshToken: action.payload.refreshToken
            };

        default:
            return state;
    }
}

interface AuthProviderProps {
    children: React.ReactNode;
}

export function AuthProvider({children}: AuthProviderProps) {
    const [state, dispatch] = useReducer(authReducer, initialState);

    const login = useCallback((tokens: TokenResponse, user: AuthUser) => {
        dispatch({
            type: 'LOGIN_SUCCESS',
            payload: {tokens, user}
        });
    }, []);

    const logout = useCallback(() => {
        dispatch({type: 'LOGOUT'});
    }, []);

    const setUser = useCallback((user: AuthUser) => {
        dispatch({type: 'SET_USER', payload: user});
    }, []);

    const refreshTokens = useCallback((tokens: TokenResponse) => {
        dispatch({type: 'REFRESH_SUCCESS', payload: tokens});
    }, []);

    const clearError = useCallback(() => {
        dispatch({type: 'CLEAR_ERROR'});
    }, []);

    const restoreTokens = useCallback(
        (accessToken: string, refreshToken: string) => {
            dispatch({
                type: 'RESTORE_TOKENS',
                payload: {accessToken, refreshToken}
            });
        },
        []
    );

    const isLoggedIn = Boolean(state.accessToken);

    const value: AuthContextType = useMemo(
        () => ({
            ...state,
            dispatch,
            login,
            logout,
            setUser,
            refreshTokens,
            clearError,
            restoreTokens,
            isLoggedIn
        }),
        [
            state,
            login,
            logout,
            setUser,
            refreshTokens,
            clearError,
            restoreTokens,
            isLoggedIn
        ]
    );

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
