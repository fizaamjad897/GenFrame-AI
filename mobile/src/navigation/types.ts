import { ResizeResult } from '../types/models';

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

export type MainTabParamList = {
  Creation: undefined;
  Transformation: undefined;
  History: undefined;
  Profile: undefined;
};

export type RootStackParamList = {
  Main: undefined;
  Result: { result: ResizeResult };
};
